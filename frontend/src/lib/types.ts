export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  first_name: string;
  last_name: string;
}

export interface Driver {
  id: number;
  user: User;
  license_number: string;
  status: string;
  pay_rate: string;
  current_truck_number?: string;
  total_miles: string;
  full_name: string;
}

export interface Trip {
  id: number;
  trip_number: string;
  status: 'ASSIGNED' | 'IN_TRANSIT' | 'DELIVERED' | 'CANCELLED';
  driver_name: string;
  truck_number: string;
  broker: string;
  load_number: string;
  origin_city: string;
  origin_state: string;
  destination_city: string;
  destination_state: string;
  scheduled_pickup: string;
  scheduled_delivery: string;
  actual_pickup?: string;
  actual_delivery?: string;
  estimated_miles: string;
  actual_miles?: string;
  rate: string;
  driver_pay: string;
  cargo_description: string;
}

export interface Document {
  id: number;
  document_type: string;
  file_name: string;
  file_url: string;
  description: string;
  uploaded_at: string;
}

export interface Payroll {
  id: number;
  pay_period_start: string;
  pay_period_end: string;
  gross_pay: string;
  net_pay: string;
  miles_driven: string;
  trips_completed: number;
  paid: boolean;
  payslip_url?: string;
}
