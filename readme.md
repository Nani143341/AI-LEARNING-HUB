
# AI Learning Hub

## Overview

The AI Learning Hub is a platform designed to provide educational resources and tools for AI enthusiasts and professionals. It offers free and premium courses, interactive quizzes, a community forum, AI-related news, and various subscription models. The platform supports user authentication, manages free and premium content based on user roles, tracks user progress, and handles payment processing for premium users.

## Features

- **User Authentication**: Users can register, log in, and manage their profiles.
- **Course Management**: Offers both free and premium courses with progress tracking.
- **Community Forum**: Users can discuss topics and share resources.
- **Payment Integration**: Handles subscription payments for premium users.
- **News Feed**: Displays the latest AI-related news.

## Technologies 

- Django (Web Framework)
- Django REST Framework (API)
- PostgreSQL (Database)
- Docker (Containerization)
- AWS Fargate (Serverless Container Hosting)
- AWS RDS (Managed PostgreSQL Database)
- AWS S3 (File Storage for media)
- AWS IAM (Identity and Access Management)

## Prerequisites

Before deploying the application, ensure you have:

- An AWS account.
- Docker installed on your machine.
- AWS CLI installed and configured with appropriate permissions.
- Python 3.8 or higher installed.

## Setup Instructions

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/ai-learning-hub.git
cd ai-learning-hub
```

### Step 2: Install Dependencies

Create a virtual environment and install the required packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the root of the project and add the following variables:

```env
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=your_domain_or_ip
DATABASE_URL=postgres://username:password@hostname:port/dbname
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=your_region
AWS_S3_CUSTOM_DOMAIN=your_custom_domain
```

### Step 4: Database Migration

Make sure to set up your PostgreSQL database in AWS RDS and update the `DATABASE_URL` in the `.env` file.

Run the following commands to apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create a Superuser

Create a superuser to access the Django admin panel:

```bash
python manage.py createsuperuser
```

### Step 6: Create Dockerfile

Create a `Dockerfile` in the root of your project:

```dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project_name.wsgi:application"]
```

### Step 7: Create Docker Compose File (Optional)

If you need to run the application locally with a database, you can create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://username:password@db:5432/dbname
    depends_on:
      - db

  db:
    image: postgres:latest
    environment:
      POSTGRES_DB: dbname
      POSTGRES_USER: username
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

### Step 8: Build and Test Locally

To build and run your Docker containers:

```bash
docker-compose up --build
```

Access the application at `http://localhost:8000`.

### Step 9: Deploy on AWS Fargate

#### 9.1 Create a Docker Image

Build your Docker image:

```bash
docker build -t ai-learning-hub .
```

#### 9.2 Push to Amazon ECR

1. **Create a new ECR repository**:

   - Go to the AWS Management Console.
   - Navigate to **ECR** and create a new repository.

2. **Authenticate Docker to your Amazon ECR**:

```bash
aws ecr get-login-password --region your_region | docker login --username AWS --password-stdin your_account_id.dkr.ecr.your_region.amazonaws.com
```

3. **Tag and push your image**:

```bash
docker tag ai-learning-hub:latest your_account_id.dkr.ecr.your_region.amazonaws.com/ai-learning-hub:latest
docker push your_account_id.dkr.ecr.your_region.amazonaws.com/ai-learning-hub:latest
```

#### 9.3 Create a New Fargate Cluster

1. Go to the AWS Management Console and navigate to **ECS**.
2. Create a new cluster (select the Fargate option).
3. Follow the prompts to create the cluster.

#### 9.4 Create a Task Definition

1. Go to the **Task Definitions** section in ECS.
2. Create a new task definition (select the Fargate option).
3. Add a container definition using the image URI from ECR and specify the port mappings (e.g., `8000`).

#### 9.5 Run the Task

1. Navigate to your cluster.
2. Click on **Tasks** and then **Run new Task**.
3. Select your task definition and run it.

#### 9.6 Configure Load Balancer (Optional)

If you want to expose your application to the internet:

1. Create an Application Load Balancer in the **EC2** section.
2. Set up listeners and target groups to route traffic to your Fargate tasks.

#### 9.7 Set Up Environment Variables in ECS

In your task definition, specify the environment variables (such as those from your `.env` file) in the container definition.

### Step 10: Access Your Application

Once the task is running and, if applicable, your load balancer is set up, you can access your application via the public URL of the load balancer.

## Conclusion

You have successfully deployed the AI Learning Hub on AWS Fargate! You can now explore its features and expand its capabilities. For further improvements, consider implementing CI/CD pipelines or integrating monitoring tools for better observability.
