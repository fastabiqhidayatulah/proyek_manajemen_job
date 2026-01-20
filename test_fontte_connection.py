#!/usr/bin/env python
"""
Test script untuk memverifikasi koneksi ke Fontte API
Format API yang benar: https://docs.fontte.com/
"""

import requests
import json
from pathlib import Path

# Konfigurasi
FONTTE_TOKEN = 'E6CwLwwzuP8Db6Dud5mn'  # Token dari settings.py
FONTTE_API_BASE_URL = 'https://api.fontte.com/v1'

def test_api_connectivity():
    """Test koneksi dasar ke Fontte API"""
    print("\n" + "="*60)
    print("1. TEST KONEKSI DASAR KE FONTTE API")
    print("="*60)
    
    try:
        headers = {
            'Authorization': f'Bearer {FONTTE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        url = f"{FONTTE_API_BASE_URL}/info"
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ BERHASIL - Koneksi OK")
            return True
        else:
            print(f"✗ GAGAL - HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ GAGAL - Request Timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ GAGAL - Connection Error")
        return False
    except Exception as e:
        print(f"✗ GAGAL - {str(e)}")
        return False


def test_send_text_message():
    """Test mengirim pesan teks ke Fontte"""
    print("\n" + "="*60)
    print("2. TEST MENGIRIM PESAN TEKS")
    print("="*60)
    
    try:
        headers = {
            'Authorization': f'Bearer {FONTTE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Format yang benar untuk Fontte API
        data = {
            'target': '62812345678-1234567890@g.us',  # Ganti dengan ID grup Anda
            'message': 'Test message dari script Python'
        }
        
        url = f"{FONTTE_API_BASE_URL}/send"
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✓ BERHASIL - Pesan terkirim")
            return True
        else:
            print(f"✗ GAGAL - HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ GAGAL - Request Timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ GAGAL - Connection Error")
        return False
    except Exception as e:
        print(f"✗ GAGAL - {str(e)}")
        return False


def test_send_file_message():
    """Test mengirim file PDF ke Fontte"""
    print("\n" + "="*60)
    print("3. TEST MENGIRIM FILE (MULTIPART)")
    print("="*60)
    
    # Buat file test dummy
    test_file_path = Path('/tmp/test_fontte.txt')
    test_file_path.write_text('Test file for Fontte API')
    
    try:
        headers = {
            'Authorization': f'Bearer {FONTTE_TOKEN}'
        }
        
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'target': '62812345678-1234567890@g.us',  # Ganti dengan ID grup Anda
                'caption': 'Test file from Django'
            }
            
            url = f"{FONTTE_API_BASE_URL}/send"
            print(f"URL: {url}")
            print(f"Data: {data}")
            print(f"File: {test_file_path}")
            
            response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✓ BERHASIL - File terkirim")
                return True
            else:
                print(f"✗ GAGAL - HTTP {response.status_code}")
                return False
        
    except requests.exceptions.Timeout:
        print("✗ GAGAL - Request Timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ GAGAL - Connection Error")
        return False
    except Exception as e:
        print(f"✗ GAGAL - {str(e)}")
        return False
    finally:
        # Cleanup
        if test_file_path.exists():
            test_file_path.unlink()


def test_get_device_info():
    """Test mendapatkan info device dari Fontte"""
    print("\n" + "="*60)
    print("4. TEST MENDAPATKAN INFO DEVICE")
    print("="*60)
    
    try:
        headers = {
            'Authorization': f'Bearer {FONTTE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        url = f"{FONTTE_API_BASE_URL}/info"
        print(f"URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Device Status: {data.get('status', 'unknown')}")
            print("✓ BERHASIL - Info device diperoleh")
            return True
        else:
            print(f"✗ GAGAL - HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ GAGAL - Request Timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ GAGAL - Connection Error")
        return False
    except Exception as e:
        print(f"✗ GAGAL - {str(e)}")
        return False


def main():
    print("\n" + "="*60)
    print("FONTTE API CONNECTION TEST")
    print("="*60)
    print(f"Token: {FONTTE_TOKEN[:10]}...")
    print(f"API URL: {FONTTE_API_BASE_URL}")
    print("\nCATATAN: Ganti nomor WA/Group ID di setiap test dengan nilai sebenarnya!")
    
    # Run tests
    test_1 = test_api_connectivity()
    test_2 = test_send_text_message()
    test_3 = test_send_file_message()
    test_4 = test_get_device_info()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"1. Koneksi Dasar: {'✓ PASSED' if test_1 else '✗ FAILED'}")
    print(f"2. Kirim Pesan: {'✓ PASSED' if test_2 else '✗ FAILED'}")
    print(f"3. Kirim File: {'✓ PASSED' if test_3 else '✗ FAILED'}")
    print(f"4. Info Device: {'✓ PASSED' if test_4 else '✗ FAILED'}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
