# ==============================================================================
# EXPORT HANDLER - SEND DATA TO GOOGLE APPS SCRIPT
# ==============================================================================
import requests
import json
from django.http import JsonResponse
from .models import Job, CustomUser
from django.db.models import Q

# Google Apps Script URLs (JANGAN DIUBAH)
GAS_PREVENTIF_URL = "https://script.google.com/macros/s/AKfycbyqbeARRivauzTinWAnKwOUglV7r1ANsLXJRTRtMpd3TSDlaIXpiRzwuul2j6reecw7/exec"
GAS_EVALUASI_URL = "https://script.google.com/macros/s/AKfycbxg2zPRso6f1bZQTuOxg2D2ey64a1iY6wWTKv-QmeZQBQIKDHjH8k2UT6wvSlgpZrOf2g/exec"


def prepare_job_data_for_export(job_ids, export_type="preventif"):
    """
    Prepare job data untuk export ke Google Apps Script
    Format disesuaikan dengan template Google Apps Script
    
    export_type: "preventif" atau "evaluasi"
    Returns: dict dengan structured data sesuai Google Apps Script template
    """
    # Fetch jobs tapi MAINTAIN urutan dari job_ids array (penting untuk sort)
    jobs_dict = {}
    jobs = Job.objects.filter(id__in=job_ids).select_related(
        'aset', 'aset__parent', 'aset__parent__parent'
    ).prefetch_related('personil_ditugaskan', 'tanggal_pelaksanaan')
    
    # Convert ke dict for ordering
    for job in jobs:
        jobs_dict[job.id] = job
    
    # Rebuild jobs list dalam urutan job_ids (PENTING: respect sort order dari frontend)
    jobs_ordered = []
    for job_id in job_ids:
        if job_id in jobs_dict:
            jobs_ordered.append(jobs_dict[job_id])
    
    if not jobs_ordered:
        return None
    
    # Ambil first job untuk tanggal (semua job seharusnya same day)
    first_job = jobs_ordered[0]
    tanggal = first_job.tanggal_pelaksanaan.first().tanggal if first_job.tanggal_pelaksanaan.exists() else None
    
    # Kumpulkan unique values
    mesin_set = set()
    sub_mesin_set = set()
    prioritas_set = set()
    job_data_list = []
    
    # Process jobs dalam urutan yang sudah di-sort (dari frontend)
    for job in jobs_ordered:
        # Collect unique mesin/sub mesin
        if job.aset:
            if job.aset.level == 2:  # Sub Mesin
                sub_mesin_set.add(job.aset.nama)
                if job.aset.parent:  # Mesin
                    mesin_set.add(job.aset.parent.nama)
            elif job.aset.level == 1:  # Mesin
                mesin_set.add(job.aset.nama)
        
        # Collect prioritas
        if job.prioritas:
            prioritas_set.add(job.get_prioritas_display())
        
        # Prepare job data row
        # Format berbeda untuk preventif vs evaluasi
        personil_names = ", ".join([p.nama_lengkap for p in job.personil_ditugaskan.all()])
        mesin_name = job.aset.parent.nama if job.aset and job.aset.level == 2 and job.aset.parent else (job.aset.nama if job.aset else "")
        sub_mesin_name = job.aset.nama if job.aset and job.aset.level == 2 else ""
        job_name = job.nama_pekerjaan
        
        if export_type == "preventif":
            # Preventif: [Personil, Mesin, SubMesin, DetailPekerjaan]
            job_data_list.append([
                personil_names,
                mesin_name,
                sub_mesin_name,
                job_name
            ])
        elif export_type == "evaluasi":
            # Evaluasi: [Personil, Mesin, SubMesin, DetailPekerjaan, Kesimpulan/Status]
            job_data_list.append([
                personil_names,
                mesin_name,
                sub_mesin_name,
                job_name,
                ""  # Kolom kesimpulan/status kosong (user isi di sheet)
            ])
    
    # Format payload sesuai Google Apps Script template
    payload = {
        "exportType": export_type,  # PENTING: Ada field ini untuk routing di Google Apps Script
        "tanggal": str(tanggal) if tanggal else "",
        "allMesin": ", ".join(sorted(mesin_set)) if mesin_set else "",
        "allSubMesin": ", ".join(sorted(sub_mesin_set)) if sub_mesin_set else "",
        "allPrioritas": ", ".join(sorted(prioritas_set)) if prioritas_set else "",
        "jobData": job_data_list
    }
    
    return payload


def prepare_unified_job_data_for_export(job_ids_with_type, export_type="preventif"):
    """
    Prepare unified job data (Daily + Project + Preventive) untuk export ke Google Apps Script
    Format disesuaikan dengan template Google Apps Script
    
    job_ids_with_type: list of strings dalam format "id_type" (e.g., ["1_daily", "2_project", "3_preventive"])
    export_type: "preventif" atau "evaluasi"
    Returns: dict dengan structured data sesuai Google Apps Script template
    """
    from preventive_jobs.models import PreventiveJobExecution
    from django.utils import timezone
    
    # Parse job IDs dengan tipe mereka
    daily_job_ids = []
    project_job_ids = []
    preventive_job_ids = []
    id_order_map = {}  # Track original order
    
    for idx, job_id_str in enumerate(job_ids_with_type):
        try:
            job_id, job_type = job_id_str.rsplit('_', 1)
            job_id = int(job_id)
            id_order_map[(job_id, job_type)] = idx
            
            if job_type == 'daily' or job_type == 'project':
                daily_job_ids.append(job_id)
            elif job_type == 'preventive':
                preventive_job_ids.append(job_id)
        except (ValueError, AttributeError):
            continue
    
    # Kumpulkan unique values
    mesin_set = set()
    sub_mesin_set = set()
    prioritas_set = set()
    job_data_list = []
    all_jobs_with_order = []  # Track jobs dengan order mereka
    
    # 1. Process Daily/Project jobs
    if daily_job_ids:
        jobs = Job.objects.filter(id__in=daily_job_ids).select_related(
            'aset', 'aset__parent', 'aset__parent__parent', 'pic', 'assigned_to'
        ).prefetch_related('personil_ditugaskan', 'tanggal_pelaksanaan')
        
        for job in jobs:
            job_type = 'project' if job.tipe_job == 'Project' else 'daily'
            order_idx = id_order_map.get((job.id, job_type), 999)
            
            # Collect unique mesin/sub mesin
            if job.aset:
                if job.aset.level == 2:
                    sub_mesin_set.add(job.aset.nama)
                    if job.aset.parent:
                        mesin_set.add(job.aset.parent.nama)
                elif job.aset.level == 1:
                    mesin_set.add(job.aset.nama)
            
            if job.prioritas:
                prioritas_set.add(job.get_prioritas_display())
            
            # Prepare job data row
            personil_names = ", ".join([p.nama_lengkap for p in job.personil_ditugaskan.all()])
            mesin_name = job.aset.parent.nama if job.aset and job.aset.level == 2 and job.aset.parent else (job.aset.nama if job.aset else "")
            sub_mesin_name = job.aset.nama if job.aset and job.aset.level == 2 else ""
            
            if export_type == "preventif":
                row = [personil_names, mesin_name, sub_mesin_name, job.nama_pekerjaan]
            elif export_type == "evaluasi":
                row = [personil_names, mesin_name, sub_mesin_name, job.nama_pekerjaan, ""]
            else:
                row = [personil_names, mesin_name, sub_mesin_name, job.nama_pekerjaan]
            
            all_jobs_with_order.append((order_idx, row))
    
    # 2. Process Preventive jobs
    if preventive_job_ids:
        executions = PreventiveJobExecution.objects.filter(id__in=preventive_job_ids).select_related(
            'template', 'template__pic', 'aset', 'aset__parent', 'aset__parent__parent', 'assigned_to'
        ).prefetch_related('assigned_to_personil')
        
        for execution in executions:
            order_idx = id_order_map.get((execution.id, 'preventive'), 999)
            
            # Collect unique mesin/sub mesin
            if execution.aset:
                if execution.aset.level == 2:
                    sub_mesin_set.add(execution.aset.nama)
                    if execution.aset.parent:
                        mesin_set.add(execution.aset.parent.nama)
                elif execution.aset.level == 1:
                    mesin_set.add(execution.aset.nama)
            
            if execution.template and execution.template.prioritas:
                prioritas_set.add(execution.template.get_prioritas_display())
            
            # Prepare job data row
            personil_names = ", ".join([p.nama_lengkap for p in execution.assigned_to_personil.all()])
            mesin_name = execution.aset.parent.nama if execution.aset and execution.aset.parent else ""
            sub_mesin_name = execution.aset.nama if execution.aset else ""
            
            if export_type == "preventif":
                row = [personil_names, mesin_name, sub_mesin_name, execution.template.nama_pekerjaan]
            elif export_type == "evaluasi":
                row = [personil_names, mesin_name, sub_mesin_name, execution.template.nama_pekerjaan, ""]
            else:
                row = [personil_names, mesin_name, sub_mesin_name, execution.template.nama_pekerjaan]
            
            all_jobs_with_order.append((order_idx, row))
    
    if not all_jobs_with_order:
        return None
    
    # Sort berdasarkan original order dari frontend
    all_jobs_with_order.sort(key=lambda x: x[0])
    job_data_list = [row for _, row in all_jobs_with_order]
    
    # Format payload sesuai Google Apps Script template (SAMA seperti prepare_job_data_for_export)
    payload = {
        "exportType": export_type,
        "tanggal": str(timezone.now().date()),
        "allMesin": ", ".join(sorted(mesin_set)) if mesin_set else "",
        "allSubMesin": ", ".join(sorted(sub_mesin_set)) if sub_mesin_set else "",
        "allPrioritas": ", ".join(sorted(prioritas_set)) if prioritas_set else "",
        "jobData": job_data_list
    }
    
    return payload


def send_to_google_apps_script(payload, export_type="preventif"):
    """
    Send payload to Google Apps Script
    
    export_type: "preventif" atau "evaluasi"
    Returns: dict dengan status dan response
    """
    if export_type == "preventif":
        gas_url = GAS_PREVENTIF_URL
    elif export_type == "evaluasi":
        gas_url = GAS_EVALUASI_URL
    else:
        return {"status": "error", "message": "Jenis export tidak dikenali"}
    
    try:
        # Send POST request ke Google Apps Script
        response = requests.post(
            gas_url,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "status": "success",
            "data": result,
            "message": result.get("message", "Data berhasil diekspor")
        }
    
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timeout - Google Apps Script tidak merespons"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Connection error - Tidak bisa terhubung ke Google Apps Script"}
    except ValueError as e:
        return {"status": "error", "message": f"Invalid JSON response dari Google Apps Script: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}



