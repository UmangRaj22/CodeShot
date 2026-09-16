# 🚀 Deployment Guide: Render

This guide explains how to deploy CodeShot on [Render](https://render.com).

## Prerequisites

- GitHub account with your repository pushed
- Render account (free tier available)
- Environment variables configured

## Step 1: Push to GitHub

```bash
cd code_shot
git init
git add .
git commit -m "Initial commit: CodeShot Django app ready for deployment"
git branch -M main
git remote add origin https://github.com/UmangRaj22/shareable-code-snippets.git
git push -u origin main
```

## Step 2: Create Render Account & Connect Repository

1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Web Service"
3. Select "Build and deploy from a Git repository"
4. Click "Connect" and authorize GitHub
5. Select your `shareable-code-snippets` repository

## Step 3: Configure Web Service

Fill in the following details:

- **Name**: `codeshot` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Select closest to your users
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn code_shot.wsgi:application --bind 0.0.0.0:$PORT`

## Step 4: Add Environment Variables

In the Render dashboard, go to "Environment" and add:

```
DEBUG=False
SECRET_KEY=<generate-a-secure-key>
ALLOWED_HOSTS=<your-app-name>.onrender.com
DATABASE_URL=<postgres-connection-string>
```

To generate a secure SECRET_KEY, run:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Step 5: Add PostgreSQL Database

1. In Render dashboard, click "New" → "PostgreSQL"
2. Fill in:
   - **Name**: `codeshot-db`
   - **Database**: `codeshot`
   - **Region**: Same as web service
   - **PostgreSQL Version**: `15`
3. Copy the `DATABASE_URL` and add it to your web service environment variables

## Step 6: Update Django Settings for Production

Your `code_shot/settings.py` should use environment variables:

```python
import os
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='unsafe-key')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='codeshot'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

Or use a single `DATABASE_URL`:
```python
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}
```

## Step 7: Run Migrations on Render

Once deployed, Render will run the `release` command in `Procfile`:
```
python manage.py migrate
```

This runs automatically before starting the web server.

## Step 8: Collect Static Files

Add to your Render build command or create a `build.sh`:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

Or manually run:
```bash
python manage.py collectstatic --noinput
```

## Step 9: Verify Deployment

1. Check Render logs for errors
2. Visit `https://<your-app-name>.onrender.com`
3. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Common Issues & Fixes

### Issue: ModuleNotFoundError
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility

### Issue: Database connection fails
- Verify `DATABASE_URL` is set correctly
- Ensure PostgreSQL service is running
- Check database credentials

### Issue: Static files not loading
- Ensure `STATIC_ROOT` and `STATIC_URL` are configured
- Run `python manage.py collectstatic --noinput`
- Use WhiteNoise or a CDN for serving static files

### Issue: Media files not persisting
- Render's filesystem is ephemeral (temporary)
- Use AWS S3 or similar cloud storage for media uploads
- Update `MEDIA_ROOT` to use cloud storage service

## Optional: Use Render.yaml for Infrastructure as Code

Instead of manual setup, Render can read `render.yaml` (included in repo):

```bash
# Deploy using render.yaml
# Just push to GitHub and Render will auto-detect and configure services
```

## Next Steps

- Set up a domain name
- Configure email (SendGrid, Gmail, etc.)
- Add CI/CD pipeline (GitHub Actions)
- Monitor performance with Render Analytics
- Set up error tracking (Sentry, etc.)

## References

- [Render Django Deployment](https://render.com/docs/deploy-django)
- [Render PostgreSQL](https://render.com/docs/databases)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)

---

**Need Help?** Check Render logs or open an issue on GitHub.
