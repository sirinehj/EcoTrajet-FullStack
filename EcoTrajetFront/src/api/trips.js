import axios from 'axios';
const API_BASE = import.meta.env.DEV 
  ? 'http://localhost:8000'
  : '';

export const tripService = {
  getTrips: async (filters = {}) => {
    try {
      const params = {
        origin: filters.departure_city,
        destination: filters.arrival_city,
        departure_time: filters.departure_date,
        status: 'SCHEDULED'
      };
      
      const response = await axios.get(`${API_BASE}/trips/`, { params });

      console.log(response.data)
      return response.data.results;
    } catch (error) {
      console.error('Error fetching trips:', error);
      throw error;
    }
  },

  createTrip: async (tripData) => {
    try {
      const response = await axios.post(`${API_BASE}/trips/`, tripData, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error creating trip:', error);
      throw error;
    }
  },

  // Get trip details
  getTripDetails: async (tripId) => {
    try {
      const response = await axios.get(`${API_BASE}/trips/${tripId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching trip details:', error);
      throw error;
    }
  },

  // Update a trip
  updateTrip: async (tripId, tripData) => {
    try {
      const response = await axios.patch(`${API_BASE}/trips/${tripId}/`, tripData, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error updating trip:', error);
      throw error;
    }
  },

  // Cancel a trip (soft delete)
  cancelTrip: async (tripId) => {
    try {
      const response = await axios.delete(`${API_BASE}/trips/${tripId}/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error cancelling trip:', error);
      throw error;
    }
  },

  // Get reservations for a trip
  getTripReservations: async (tripId) => {
    try {
      const response = await axios.get(`${API_BASE}/trips/${tripId}/reservations/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching trip reservations:', error);
      throw error;
    }
  }
};