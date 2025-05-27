# Deploying PDF & Word Converter to Vercel

This guide will walk you through deploying your PDF & Word Converter application to Vercel.

## Prerequisites

1. A [Vercel](https://vercel.com) account
2. [Git](https://git-scm.com/downloads) installed on your computer
3. [Vercel CLI](https://vercel.com/download) (optional, but recommended)

## Deployment Steps

### 1. Initialize a Git Repository

```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Follow the instructions to push your existing repository to GitHub

### 3. Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard

1. Log in to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - Framework Preset: Other
   - Build Command: Leave empty
   - Output Directory: Leave empty
5. Click "Deploy"

#### Option B: Deploy via Vercel CLI

1. Install Vercel CLI if you haven't already:
   ```bash
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```bash
   vercel login
   ```

3. Deploy the project:
   ```bash
   vercel
   ```

4. Follow the prompts to configure your project

## Important Notes

### Limitations of This Approach

1. **Temporary Storage**: This version uses in-memory storage which is not persistent. Files will be lost when the serverless function restarts.

2. **Cold Starts**: Serverless functions may experience "cold starts" which can delay the first request.

3. **Execution Time Limits**: Vercel has a 10-second execution time limit for serverless functions. Large file conversions may time out.

### Production Recommendations

For a production-ready application, consider these improvements:

1. **Use Cloud Storage**: Implement AWS S3, Firebase Storage, or similar for file storage.

2. **Add Authentication**: Protect your application from abuse with user authentication.

3. **Implement Rate Limiting**: Prevent excessive usage of your application.

4. **Set Up a Custom Domain**: Configure a custom domain for your application.

## Troubleshooting

If you encounter issues during deployment:

1. Check Vercel's function logs in the Vercel Dashboard
2. Ensure all dependencies are correctly listed in requirements.txt
3. Verify that your vercel.json configuration is correct
