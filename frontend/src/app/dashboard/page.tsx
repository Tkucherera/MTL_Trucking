'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Truck,
  MapPin,
  Clock,
  DollarSign,
  FileText,
  LogOut,
  Menu,
  X,
  Navigation,
  Package,
  TrendingUp,
} from 'lucide-react';
import { useAuthStore } from '@/lib/store';
import { driverApi, tripApi, authApi } from '@/lib/api';
import { Trip, Document, Payroll } from '@/lib/types';
import { format } from 'date-fns';

export default function DashboardPage() {
  const router = useRouter();
  const { user, driver, logout, loadFromStorage } = useAuthStore();
  const [currentTrip, setCurrentTrip] = useState<Trip | null>(null);
  const [recentTrips, setRecentTrips] = useState<Trip[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [payroll, setPayroll] = useState<Payroll[]>([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'trips' | 'documents' | 'payroll'>('overview');

  useEffect(() => {
    loadFromStorage();
  }, [loadFromStorage]);

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    fetchData();
  }, [user, router]);

  const fetchData = async () => {
    try {
      const [currentTripRes, tripsRes, docsRes] = await Promise.all([
        driverApi.getCurrentTrip(),
        driverApi.getTrips(),
        driver ? driverApi.getDocuments(driver.id) : Promise.resolve({ data: [] }),
      ]);

      if (currentTripRes.data && currentTripRes.data.id) {
        setCurrentTrip(currentTripRes.data);
      } else {
        setCurrentTrip(null);
      }

      setRecentTrips(tripsRes.data.slice(0, 5));
      setDocuments(docsRes.data.slice(0, 5));

      if (driver) {
        const payrollRes = await driverApi.getPayroll(driver.id);
        setPayroll(payrollRes.data.slice(0, 3));
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      logout();
      router.push('/login');
    }
  };

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

  const updateTripStatus = async (tripId: number, status: string) => {
    try {
      await tripApi.updateStatus(tripId, {
        status,
        notes: `Status updated to ${status}`,
      });
      fetchData();
    } catch (error) {
      console.error('Error updating trip status:', error);
      alert('Failed to update trip status');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden mr-4 p-2 rounded-lg hover:bg-gray-100"
              >
                {sidebarOpen ? <X /> : <Menu />}
              </button>
              <div className="flex items-center">
                <Truck className="w-8 h-8 text-primary-600" />
                <span className="ml-3 text-xl font-bold text-gray-900">Driver Portal</span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {driver?.full_name || user?.first_name}
                </p>
                <p className="text-xs text-gray-600">{driver?.status}</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg hover:bg-gray-100 text-gray-600"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Miles</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {parseFloat(driver?.total_miles || '0').toLocaleString()}
                </p>
              </div>
              <div className="p-3 bg-primary-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-primary-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Current Truck</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {driver?.current_truck_number || 'None'}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Truck className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pay Rate</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  ${driver?.pay_rate}/mi
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Trips</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {recentTrips.length}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <Package className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Current Trip Alert */}
        {currentTrip && (
          <div className="card mb-8 bg-gradient-to-r from-primary-50 to-blue-50 border-l-4 border-primary-600">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center flex-wrap mb-2">
                  <Navigation className="w-5 h-5 text-primary-600 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    Active Trip: {currentTrip.trip_number}
                  </h3>
                  <span className={`ml-3 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(currentTrip.status)}`}>
                    {currentTrip.status.replace('_', ' ')}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">From</p>
                    <p className="font-medium">
                      {currentTrip.origin_city}, {currentTrip.origin_state}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">To</p>
                    <p className="font-medium">
                      {currentTrip.destination_city}, {currentTrip.destination_state}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Pickup</p>
                    <p className="font-medium">
                      {format(new Date(currentTrip.scheduled_pickup), 'MMM dd, yyyy HH:mm')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Delivery</p>
                    <p className="font-medium">
                      {format(new Date(currentTrip.scheduled_delivery), 'MMM dd, yyyy HH:mm')}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                {currentTrip.status === 'ASSIGNED' && (
                  <button
                    onClick={() => updateTripStatus(currentTrip.id, 'IN_TRANSIT')}
                    className="btn-primary whitespace-nowrap w-full lg:w-auto"
                  >
                    Start Trip
                  </button>
                )}
                {currentTrip.status === 'IN_TRANSIT' && (
                  <button
                    onClick={() => updateTripStatus(currentTrip.id, 'DELIVERED')}
                    className="btn-primary whitespace-nowrap w-full lg:w-auto"
                  >
                    Mark Delivered
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200 overflow-x-auto">
            <nav className="-mb-px flex space-x-8">
              {['overview', 'trips', 'documents', 'payroll'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm capitalize whitespace-nowrap ${
                    activeTab === tab
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Trips */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Recent Trips</h3>
              <div className="space-y-4">
                {recentTrips.length > 0 ? (
                  recentTrips.map((trip) => (
                    <div
                      key={trip.id}
                      className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <p className="font-medium text-gray-900">{trip.trip_number}</p>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(trip.status)}`}>
                          {trip.status.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        {trip.origin_city} → {trip.destination_city}
                      </p>
                      <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                        <span>{format(new Date(trip.scheduled_pickup), 'MMM dd')}</span>
                        <span>{trip.estimated_miles} mi</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-8">No trips found</p>
                )}
              </div>
            </div>

            {/* Recent Documents */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Recent Documents</h3>
              <div className="space-y-3">
                {documents.length > 0 ? (
                  documents.map((doc) => (
                    <a
                      key={doc.id}
                      href={doc.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <FileText className="w-5 h-5 text-primary-600 mr-3 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">{doc.file_name}</p>
                        <p className="text-xs text-gray-500">{doc.document_type}</p>
                      </div>
                    </a>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-8">No documents found</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trips' && (
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">All Trips</h3>
            <div className="space-y-4">
              {recentTrips.length > 0 ? (
                recentTrips.map((trip) => (
                  <div key={trip.id} className="p-6 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start mb-4 flex-wrap gap-2">
                      <div>
                        <h4 className="font-semibold text-lg">{trip.trip_number}</h4>
                        <p className="text-sm text-gray-600">{trip.broker}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(trip.status)}`}>
                        {trip.status.replace('_', ' ')}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">Origin</p>
                        <p className="font-medium">{trip.origin_city}, {trip.origin_state}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Destination</p>
                        <p className="font-medium">{trip.destination_city}, {trip.destination_state}</p>
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row sm:justify-between text-sm gap-2">
                      <span className="text-gray-600">
                        {trip.estimated_miles} miles • ${trip.driver_pay}
                      </span>
                      <span className="text-gray-600">
                        {format(new Date(trip.scheduled_pickup), 'MMM dd, yyyy')}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">No trips found</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">All Documents</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {documents.length > 0 ? (
                documents.map((doc) => (
                  <a
                    key={doc.id}
                    href={doc.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-start">
                      <FileText className="w-6 h-6 text-primary-600 mr-3 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{doc.file_name}</p>
                        <p className="text-sm text-gray-600 mt-1">{doc.document_type}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {format(new Date(doc.uploaded_at), 'MMM dd, yyyy')}
                        </p>
                      </div>
                    </div>
                  </a>
                ))
              ) : (
                <div className="col-span-2 text-gray-500 text-center py-8">No documents found</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'payroll' && (
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Payroll History</h3>
            <div className="space-y-4">
              {payroll.length > 0 ? (
                payroll.map((record) => (
                  <div key={record.id} className="p-6 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start mb-4 flex-wrap gap-2">
                      <div>
                        <p className="font-semibold">
                          {format(new Date(record.pay_period_start), 'MMM dd')} -{' '}
                          {format(new Date(record.pay_period_end), 'MMM dd, yyyy')}
                        </p>
                        <p className="text-sm text-gray-600">
                          {record.trips_completed} trips • {record.miles_driven} miles
                        </p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        record.paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {record.paid ? 'Paid' : 'Pending'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Gross Pay</p>
                        <p className="text-lg font-semibold text-gray-900">${record.gross_pay}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Net Pay</p>
                        <p className="text-lg font-semibold text-green-600">${record.net_pay}</p>
                      </div>
                    </div>

                    {record.payslip_url && (
                      <a
                        href={record.payslip_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-4 inline-flex items-center text-sm text-primary-600 hover:text-primary-700"
                      >
                        <FileText className="w-4 h-4 mr-1" />
                        View Payslip
                      </a>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">No payroll records found</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}