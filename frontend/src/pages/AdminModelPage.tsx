import React, { useEffect, useState } from 'react';
import { ModelDeployment } from '../types';
import axios from 'axios';

const AdminModelPage: React.FC = () => {
  const [models, setModels] = useState<ModelDeployment[]>([]);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get('/api/v1/models');
        setModels(response.data);
      } catch (error) {
        console.error('Failed to fetch models', error);
      }
    };

    fetchModels();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Model Deployments</h1>
      <div className="space-y-4">
        {models.map((model) => (
          <div key={model.id} className="border p-4 rounded shadow-sm bg-white">
            <h2 className="font-bold">Version: {model.model_version}</h2>
            <p>Status: {model.status}</p>
            <p>Accuracy: {model.metrics?.accuracy ?? 'N/A'}</p>
            <p>Deployed by User ID: {model.deployed_by}</p>
            <p>Time: {new Date(model.deployment_time).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdminModelPage;
