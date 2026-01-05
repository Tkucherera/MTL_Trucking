# Trucking Company API - Django REST Framework

A comprehensive REST API for managing trucking company operations including drivers, trucks, trips, payroll, and document management.

## Features

### Authentication
- **Username/Password**: Standard authentication with JWT tokens
- **OTP/2FA**: Time-based one-time passwords via authenticator apps
- **Email OTP**: One-time passwords sent via email
- **Passkey**: WebAuthn/FIDO2 passkey authentication
- **Session Tokens**: JWT-based access and refresh tokens

### Core Features
- **Driver Management**: Track drivers, licenses, CDL, status, and assignments
- **Trip Management**: Complete trip lifecycle from assignment to delivery
- **Truck Management**: Fleet tracking and maintenance scheduling
- **Mileage Tracking**: Per-trip mileage tracking for each driver
- **Route Tracking**: GPS coordinates stored for each trip
- **Document Management**: Store licenses, CDL, payslips, BOL, POD, etc.
- **Payroll**: Track earnings, deductions, and generate payslips
- **Real-time Updates**: Trip status updates with location tracking

### Role-Based Access Control
- **Admin**: Full access to all resources
- **Driver**: Access to own profile, trips, documents, and payroll
- **Staff**: Configurable access (extendable)

## Setup Instructions

### 1. Prerequisites
```bash
Python 3.10+
PostgreSQL 13+
```

### 2. Installation

```bash
# Clone repository
git clone <repository-url>
cd trucking-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration

Create PostgreSQL database:
```sql
CREATE DATABASE trucking_db;
CREATE USER trucking_user WITH PASSWORD 'your_password';
ALTER ROLE trucking_user SET client_encoding TO 'utf8';
ALTER ROLE trucking_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE trucking_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE trucking_db TO trucking_user;
GRANT USAGE, CREATE ON SCHEMA public TO trucking_user;
```

Update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trucking_db',
        'USER': 'trucking_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Server

```bash
python manage.py runserver
```

API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication

#### Login (Username/Password)
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "driver1",
  "password": "password123"
}

Response:
{
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "username": "driver1",
    "email": "driver1@example.com",
    "role": "DRIVER",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Setup OTP/2FA
```http
POST /api/auth/otp/setup/
Authorization: Bearer <access_token>

Response:
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,...",
  "provisioning_uri": "otpauth://totp/..."
}
```

#### Verify OTP Setup
```http
POST /api/auth/otp/verify/
Authorization: Bearer <access_token>

{
  "otp_code": "123456"
}
```

#### Request Email OTP
```http
POST /api/auth/otp/email/
Content-Type: application/json

{
  "email": "driver@example.com"
}
```

#### Login with Email OTP
```http
POST /api/auth/otp/email/verify/

{
  "email": "driver@example.com",
  "otp_code": "123456"
}
```

#### Register Passkey
```http
POST /api/auth/passkey/register/
Authorization: Bearer <access_token>

{
  "credential_id": "base64_credential_id",
  "public_key": "base64_public_key"
}
```

### Driver Endpoints

#### List Drivers (Admin only)
```http
GET /api/drivers/
Authorization: Bearer <access_token>
```

#### Create Driver (Admin/Staff only)
```http
POST /api/drivers/
Authorization: Bearer <access_token>

{
  "user": {
    "username": "newdriver",
    "email": "newdriver@example.com",
    "password": "securepass123",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "555-0123",
    "role": "DRIVER"
  },
  "license_number": "DL123456",
  "license_expiry": "2026-12-31",
  "cdl_class": "A",
  "cdl_expiry": "2026-12-31",
  "pay_rate": "0.55",
  "emergency_contact_name": "John Smith",
  "emergency_contact_phone": "555-0199"
}
```

#### Get Current Driver Profile
```http
GET /api/drivers/me/
Authorization: Bearer <access_token>
```

#### Get Driver Mileage Per Trip
```http
GET /api/drivers/{id}/mileage/
Authorization: Bearer <access_token>

Response:
[
  {
    "trip_id": 123,
    "trip_number": "TRP-2024-001",
    "actual_miles": 450.5,
    "origin": "Los Angeles",
    "destination": "San Francisco",
    "completed_date": "2024-01-15T14:30:00Z"
  }
]
```

#### Assign Truck to Driver (Admin only)
```http
POST /api/drivers/{id}/assign_truck/
Authorization: Bearer <access_token>

{
  "truck_id": 5
}
```

#### Get Driver's Payroll
```http
GET /api/drivers/{id}/payroll/
Authorization: Bearer <access_token>
```

#### Get Driver's Documents
```http
GET /api/drivers/{id}/documents/?type=LICENSE
Authorization: Bearer <access_token>
```

### Trip Endpoints

#### List Trips
```http
GET /api/trips/?status=IN_TRANSIT&broker=ABC%20Logistics
Authorization: Bearer <access_token>
```

#### Create Trip
```http
POST /api/trips/
Authorization: Bearer <access_token>

{
  "driver": 1,
  "truck": 2,
  "broker": "ABC Logistics",
  "load_number": "LOAD12345",
  "origin_address": "123 Main St",
  "origin_city": "Los Angeles",
  "origin_state": "CA",
  "origin_zip": "90001",
  "destination_address": "456 Oak Ave",
  "destination_city": "San Francisco",
  "destination_state": "CA",
  "destination_zip": "94102",
  "scheduled_pickup": "2024-01-20T08:00:00Z",
  "scheduled_delivery": "2024-01-21T16:00:00Z",
  "rate": "2500.00",
  "driver_pay": "1400.00",
  "estimated_miles": 382.5,
  "cargo_description": "Electronics",
  "cargo_weight": "15000.00"
}
```

#### Get Driver's Trips
```http
GET /api/trips/my_trips/
Authorization: Bearer <access_token>
```

#### Get Current Active Trip
```http
GET /api/trips/current_trip/
Authorization: Bearer <access_token>

Response:
{
  "id": 123,
  "trip_number": "TRP-2024-001",
  "status": "IN_TRANSIT",
  "driver_name": "John Doe",
  "truck_number": "TRK-001",
  ...
}
```

#### Update Trip Status
```http
POST /api/trips/{id}/update_status/
Authorization: Bearer <access_token>

{
  "status": "IN_TRANSIT",
  "notes": "Loaded and departed warehouse",
  "location": "Las Vegas, NV",
  "latitude": 36.1699,
  "longitude": -115.1398
}
```

#### Add Route Point (GPS Tracking)
```http
POST /api/trips/{id}/add_route_point/
Authorization: Bearer <access_token>

{
  "latitude": 34.0522,
  "longitude": -118.2437,
  "speed": 65.5,
  "heading": 45.2
}
```

#### Get Trip Route
```http
GET /api/trips/{id}/route/
Authorization: Bearer <access_token>

Response:
[
  {
    "id": 1,
    "latitude": "34.0522000",
    "longitude": "-118.2437000",
    "timestamp": "2024-01-20T10:15:00Z",
    "speed": "65.50",
    "heading": "45.20"
  }
]
```

#### Get Trip Updates
```http
GET /api/trips/{id}/updates/
Authorization: Bearer <access_token>
```

#### Assign Trip (Admin only)
```http
POST /api/trips/{id}/assign/
Authorization: Bearer <access_token>

{
  "driver_id": 1,
  "truck_id": 2
}
```

### Truck Endpoints (Admin Only)

#### List Trucks
```http
GET /api/trucks/?status=AVAILABLE
Authorization: Bearer <access_token>
```

#### Create Truck
```http
POST /api/trucks/
Authorization: Bearer <access_token>

{
  "truck_number": "TRK-010",
  "make": "Freightliner",
  "model": "Cascadia",
  "year": 2022,
  "vin": "1FUJGEDV1NLDXXXXX",
  "license_plate": "CA1234ABC",
  "status": "AVAILABLE",
  "fuel_capacity": "200.00",
  "gps_device_id": "GPS12345"
}
```

#### Get Available Trucks
```http
GET /api/trucks/available/
Authorization: Bearer <access_token>
```

#### Mark Truck for Maintenance
```http
POST /api/trucks/{id}/maintenance/
Authorization: Bearer <access_token>

{
  "next_maintenance_due": "2024-06-15"
}
```

### Document Endpoints

#### Upload Document
```http
POST /api/documents/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

driver: 1
document_type: LICENSE
file: <file_upload>
description: Driver's license renewal
```

#### List Documents
```http
GET /api/documents/?driver_id=1&type=PAYSLIP
Authorization: Bearer <access_token>
```

### Payroll Endpoints

#### List Payroll Records
```http
GET /api/payroll/?driver_id=1
Authorization: Bearer <access_token>
```

#### Create Payroll Record (Admin only)
```http
POST /api/payroll/
Authorization: Bearer <access_token>

{
  "driver": 1,
  "pay_period_start": "2024-01-01",
  "pay_period_end": "2024-01-15",
  "base_pay": "2000.00",
  "mileage_pay": "825.00",
  "bonus": "100.00",
  "taxes": "730.00",
  "insurance": "150.00",
  "other_deductions": "45.00",
  "gross_pay": "2925.00",
  "net_pay": "2000.00",
  "miles_driven": "1500.00",
  "trips_completed": 5
}
```

## Database Schema

### Key Relationships
- **User** → **Driver** (One-to-One)
- **Driver** → **Truck** (Many-to-One, current assignment)
- **Trip** → **Driver** (Many-to-One)
- **Trip** → **Truck** (Many-to-One)
- **Trip** → **RoutePoint** (One-to-Many)
- **Trip** → **TripUpdate** (One-to-Many)
- **Driver** → **Document** (One-to-Many)
- **Driver** → **Payroll** (One-to-Many)

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Role-Based Access Control**: Admin, Driver, Staff roles
3. **Password Hashing**: Django's built-in PBKDF2 algorithm
4. **OTP/2FA**: Additional security layer
5. **Token Blacklisting**: Logout invalidates tokens
6. **CORS Configuration**: Restrict cross-origin requests

## Future Enhancements

1. **Real-time GPS Tracking**: WebSocket integration for live location updates
2. **Geofencing**: Alerts when trucks enter/exit specific areas
3. **Fuel Management**: Track fuel purchases and efficiency
4. **Maintenance Scheduling**: Automated maintenance reminders
5. **Invoice Generation**: Automated billing for completed trips
6. **Analytics Dashboard**: Reports on driver performance, truck utilization
7. **Mobile App**: React Native app for drivers
8. **Notifications**: Push notifications for trip assignments, updates

## Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment Considerations

### Environment Variables
Create `.env` file:
```
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/trucking_db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Production Settings
- Use environment variables for sensitive data
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Use production-grade WSGI server (Gunicorn)
- Set up SSL/TLS certificates
- Configure proper CORS settings
- Use managed PostgreSQL service
- Set up file storage (AWS S3, etc.)
- Configure Celery for background tasks
- Set up monitoring and logging

## Support

For issues and questions, please contact the development team.

## License

Proprietary - All rights reserved