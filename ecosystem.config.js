module.exports = {
  apps: [

    {
      name: "management-django",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "manage.py runserver 0.0.0.0:4321",
      interpreter: "none",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "500M",
      output: "C:/logs/management-job/django.log",
      error: "C:/logs/management-job/django-error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    },

    {
      name: "management-celery-worker",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "-m celery -A config worker -l info",
      interpreter: "none",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "500M",
      output: "C:/logs/management-job/celery-worker.log",
      error: "C:/logs/management-job/celery-worker-error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    },

    {
      name: "management-celery-beat",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "-m celery -A config beat -l info",
      interpreter: "none",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "300M",
      output: "C:/logs/management-job/celery-beat.log",
      error: "C:/logs/management-job/celery-beat-error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    },
{
  name: "grafana",

  cwd: "C:\\apps\\grafana\\bin",

  script: "grafana.exe",

  args: "server --config C:\\apps\\grafana\\conf\\custom.ini",

  interpreter: "none",

  autorestart: true,
  restart_delay: 5000,

  max_memory_restart: "500M",

  output: "C:/logs/grafana/grafana.log",
  error: "C:/logs/grafana/grafana-error.log",

  log_date_format: "YYYY-MM-DD HH:mm:ss Z"
}

  ]
};