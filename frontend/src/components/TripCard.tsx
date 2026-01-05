'use client';

import { MapPin, Clock, DollarSign } from 'lucide-react';
import { format } from 'date-fns';
import { Trip } from '@/lib/types';

interface TripCardProps {
  trip: Trip;
  onStatusUpdate?: (tripId: number, status: string) => void;
}

export default function TripCard({ trip, onStatusUpdate }: TripCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ASSIGNED':
        return 'bg-blue-100 text-blue-800';
      case 'IN_TRANSIT':
        return 'bg-yellow-100 text-yellow-800';
      case 'DELIVERED':
        return 'bg-green-100 text-green-800';
      case 'CANCELLED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{trip.trip_number}</h3>
          <p className="text-sm text-gray-600">{trip.broker}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(trip.status)}`}>
          {trip.status.replace('_', ' ')}
        </span>
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex items-start">
          <MapPin className="w-5 h-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-gray-900">
              {trip.origin_city}, {trip.origin_state}
            </p>
            <p className="text-xs text-gray-500">Pickup</p>
          </div>
        </div>

        <div className="flex items-start">
          <MapPin className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-gray-900">
              {trip.destination_city}, {trip.destination_state}
            </p>
            <p className="text-xs text-gray-500">Delivery</p>
          </div>
        </div>

        <div className="flex items-center text-sm text-gray-600">
          <Clock className="w-4 h-4 mr-2" />
          <span>{format(new Date(trip.scheduled_pickup), 'MMM dd, yyyy HH:mm')}</span>
        </div>

        <div className="flex items-center text-sm text-gray-600">
          <DollarSign className="w-4 h-4 mr-2" />
          <span>{trip.estimated_miles} miles • ${trip.driver_pay}</span>
        </div>
      </div>

      {onStatusUpdate && (
        <div className="flex gap-2">
          {trip.status === 'ASSIGNED' && (
            <button
              onClick={() => onStatusUpdate(trip.id, 'IN_TRANSIT')}
              className="btn-primary flex-1"
            >
              Start Trip
            </button>
          )}
          {trip.status === 'IN_TRANSIT' && (
            <button
              onClick={() => onStatusUpdate(trip.id, 'DELIVERED')}
              className="btn-primary flex-1"
            >
              Mark Delivered
            </button>
          )}
        </div>
      )}
    </div>
  );
}