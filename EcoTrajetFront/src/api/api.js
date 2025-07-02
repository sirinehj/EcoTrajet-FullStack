const API_BASE_URL = 'http://localhost:8000';

export const fetchData = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/endpoint/`);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};