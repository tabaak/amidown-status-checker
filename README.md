# AmIDown 🕵️‍♂️
**Stealth Website Status Monitor**

AmIDown is a modern, lightweight, and stealthy website monitoring tool. It allows you to check if a website is reachable from multiple regions while mimicking real browser behavior to bypass simple bot protection and CDN filters (like Cloudflare).

**🌐 Live Demo:** [amidown.vokh.dev](https://amidown.vokh.dev)

![AmIDown Preview](https://amidown.vokh.dev/logo.png)

## ✨ Features

- **Multi-Region Awareness**: Designed to run on AWS Lambda across different regions (Frankfurt, Singapore, N. Virginia).
- **Stealth Mode**: Uses browser-disguise headers and intelligent request fallbacks (HEAD -> GET) to ensure accurate "Up" status even for protected sites.
- **Real-time Latency**: Measures response time in milliseconds.
- **Status Classification**: Distinguishes between "Success", "Reachable with Warnings" (e.g., 403 Forbidden but reachable), and "Down".
- **Modern UI**: Clean, responsive dashboard built with React 19.

## 🛠 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework.
- **httpx**: Modern HTTP client for Python with full async support.
- **Mangum**: Adapter for running ASGI applications on AWS Lambda.
- **AWS Lambda**: Serverless execution in multiple regions.

### Frontend
- **React 19**: Modern UI library.
- **CSS3**: Custom styling with glassmorphism and smooth animations.

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.9+)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tabaak/amidown-status-checker.git
   cd amidown-status-checker
   ```

2. **Setup Backend**
   ```bash
   cd aws_lambda
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd client
   npm install
   ```

## ⚙️ Configuration

Create a `.env` file in the root directory with the following variables:

```env
# API Keys for different regions
REACT_APP_FRANKFURT_API_KEY=your_key_here
REACT_APP_SINGAPORE_API_KEY=your_key_here
REACT_APP_VIRGINIA_API_KEY=your_key_here

# Allowed CORS domains (comma separated)
DOMAINS=http://localhost:3000,https://yourdomain.com
```

## 📁 Project Structure

```
aws_lambda/        # FastAPI backend deployed to AWS Lambda
client/
  public/          # Source template for index.html: NOT deployable on its own
  src/             # React source code
  build/           # Production output from `npm run build` (git-ignored): this is what gets deployed
python/            # Lambda dependencies installed for Linux (git-ignored)
```

> [!WARNING]
> `client/public/index.html` is a **template**. It contains `%PUBLIC_URL%` placeholders and no `<script>` tags. The build step fills these in and links the bundled JS and CSS. Uploading it directly serves a blank page. Always deploy the contents of `client/build/`.

## ☁️ Deployment (Frontend: S3 + CloudFront)

1. **Build the production bundle**:
   ```bash
   cd client
   npm run build
   ```
2. **Upload the contents of `client/build/`** (not the folder itself, and never `client/public/`) to the root of the S3 bucket behind the site:
   - `index.html`, `asset-manifest.json`, `logo.png`
   - the whole `static/` folder

   With the AWS CLI:
   ```bash
   aws s3 sync build/ s3://<your-bucket>/
   ```
   Before uploading, make sure the bucket is the one the CloudFront distribution reads from: **CloudFront → Distribution → Origins → Origin domain**. The origin *name* can differ from the bucket name.
3. **Invalidate the CloudFront cache** so the new `index.html` is served:
   ```bash
   aws cloudfront create-invalidation --distribution-id <your-distribution-id> --paths "/*"
   ```

## ☁️ Deployment (Backend: AWS Lambda)

To deploy the backend, you need to package the dependencies:

1. **Prepare dependencies for Lambda Layer/Package**:
   > [!IMPORTANT]
   > AWS Lambda requires dependencies compiled for Linux. If you are developing on another platform, you must specify the platform and architecture:
   
   **For ARM64 Lambda (Recommended):**
   ```bash
   pip install --platform manylinux2014_aarch64 --only-binary=:all: -t ../python -r requirements.txt
   ```
   **For x86_64 Lambda:**
   ```bash
   pip install --platform manylinux2014_x86_64 --only-binary=:all: -t ../python -r requirements.txt
   ```

2. **Deploy**: Upload `handler_fastapi.py`, `config.py`, and the generated `python/` folder (or zip them) to AWS Lambda.

3. **Configuration**: 
   - Set the `AWS_REGION` environment variable in each Lambda instance.
   - Configure the `x-api-key` in AWS API Gateway for security.

## 📄 License
MIT License - feel free to use and modify for your own projects!
