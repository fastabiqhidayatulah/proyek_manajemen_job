module.exports = {
  apps: [
    {
      name: 'gunicorn',
      script: 'run_gunicorn.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M'
    },
    {
      name: 'celery-worker',
      script: 'run_celery_worker.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      autorestart: true,
      watch: false,
      max_memory_restart: '700M'
    },
    {
      name: 'celery-beat',
      script: 'run_celery_beat.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M'
    }
  ]
};
