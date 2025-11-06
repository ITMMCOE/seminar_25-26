import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function VerifyCredential() {
  const { credentialId } = useParams();
  const [credential, setCredential] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    verifyCredential();
  }, [credentialId]);

  const verifyCredential = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/credentials/${credentialId}/verify`);
      setCredential(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to verify credential');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verifying credential on blockchain...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="h-20 w-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="h-10 w-10 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Verification Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Success Banner */}
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-8 text-white text-center">
            <div className="h-20 w-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold mb-2">Credential Verified ✓</h2>
            <p className="text-green-100">This credential is authentic and verified on the blockchain</p>
          </div>

          {/* Credential Details */}
          <div className="p-8">
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Credential Information</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Student Name</p>
                  <p className="text-lg font-semibold text-gray-900">{credential.metadata.student_name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Degree/Course</p>
                  <p className="text-lg font-semibold text-gray-900">{credential.metadata.degree}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Institution</p>
                  <p className="text-lg font-semibold text-gray-900">{credential.metadata.institution}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Graduation Year</p>
                  <p className="text-lg font-semibold text-gray-900">{credential.metadata.graduation_year}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Grade/CGPA</p>
                  <p className="text-lg font-semibold text-gray-900">{credential.metadata.grade}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Issued Date</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {new Date(credential.metadata.issued_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Blockchain Details */}
            <div className="mb-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Blockchain Details</h3>
              <div className="bg-gray-50 rounded-xl p-6 space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Token ID</p>
                  <p className="text-lg font-mono text-gray-900">#{credential.token_id}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Owner Wallet Address</p>
                  <p className="text-sm font-mono text-gray-900 break-all">{credential.owner_wallet}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Transaction Hash</p>
                  <p className="text-sm font-mono text-gray-900 break-all">{credential.transaction_hash}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">IPFS Content ID (CID)</p>
                  <p className="text-sm font-mono text-gray-900 break-all">{credential.ipfs_cid}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Network</p>
                  <p className="text-sm text-gray-900">{credential.blockchain_verification.network}</p>
                </div>
              </div>
            </div>

            {/* Verification Status */}
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
              <div className="flex items-start">
                <svg className="h-6 w-6 text-green-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <div className="ml-3">
                  <h4 className="text-sm font-semibold text-green-900 mb-1">Blockchain Verification</h4>
                  <p className="text-sm text-green-800">
                    This credential has been verified on the blockchain. The NFT token exists and all data is authentic.
                    The marksheet document is securely stored on IPFS with hash verification.
                  </p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 flex space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
              >
                Go to Dashboard
              </button>
              <button
                onClick={() => window.print()}
                className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
              >
                Print Certificate
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default VerifyCredential;
