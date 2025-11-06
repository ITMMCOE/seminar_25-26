# CrediFi

# Academic Credential Management dApp (CrediFi)

CrediFi is a proof-of-concept decentralized application (dApp) designed to modernize the management of academic credentials. It leverages blockchain technology to create a secure, transparent, and student-owned system for issuing, managing, and verifying academic records like marksheets and certificates.

This project replaces traditional, inefficient systems with a digital-first approach, reducing fraud and administrative overhead while empowering students with control over their own data.

## Features

- **User Authentication**: Secure user registration and login system using JWT.
- **Decentralized Credential Issuance**: Universities can issue academic credentials as unique, non-fungible tokens (NFTs) on the blockchain.
- **Student-Owned Digital Wallet**: Students can view and manage their academic credentials in a secure digital profile.
- **Verifiable Credentials**: Employers and other institutions can seamlessly verify the authenticity of a credential against the blockchain.
- **Decentralized Storage**: Utilizes IPFS for secure and distributed storage of the actual credential documents.

## Tech Stack 🛠️

- **Frontend**: React.js
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Blockchain**: Ethereum (Sepolia Testnet)
- **Decentralized Storage**: IPFS (InterPlanetary File System)
- **Authentication**: JSON Web Tokens (JWT)

## Prerequisites

Before you begin, ensure you have the following installed on your local machine:

- [Node.js](https://nodejs.org/) (v16 or later recommended)
- [Python](https://www.python.org/) (v3.8 or later)
- [MongoDB](https://www.mongodb.com/try/download/community)
- [Git](https://git-scm.com/)

---

## Setup and Installation

Follow these steps to get your development environment set up.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd academic-credential-dapp


#Backend Setup\
# Navigate to the backend directory\\
cd backend

# Create a Python virtual environment\\
python -m venv venv

# Activate the virtual environment\\
# On Windows:\\
venv\Scripts\activate\\
# On macOS/Linux:\\
source venv/bin/activate

# Install the required Python packages\\
pip install -r requirements.txt

# Create a .env file in the 'backend' directory\\
# and add the following environment variables:\\
# SECRET_KEY=your_super_secret_key\\
# MONGO_URI=mongodb://localhost:27017/\\
# ALGORITHM=HS256\\
# ACCESS_TOKEN_EXPIRE_MINUTES=30

#Frontend Setup\
# Navigate to the frontend directory from the root\\
cd frontend

# Install the required npm packages\\
npm install

#Start Backend Server\
# From ./backend/\\
uvicorn server:app --reload

#Start Frontend Server\
# From ./frontend/\\
npm start

Project Structure\
-----------------

The project is organized into two main folders:

-   `📁 backend/`: Contains the FastAPI application, server logic, database models, and API endpoints.

-   `📁 frontend/`: Contains the React application, components, services, and all UI-related code.

You are now all set to run and test the Academic Credential Management dApp locally!
```
