# 24f1000225
college project


🚗 Vehicle Parking System – Project Description

📌 Overview:
    The Vehicle Parking System is a role-based web application developed to efficiently manage vehicle parking slots within a premises or multi-level parking area. The application caters to both administrators and end users, providing tailored dashboards, data visualizations, and secure authentication to streamline parking operations and enhance user experience.

🎯 Key Objectives:

    Automate the management of parking lots and bookings.

    Provide role-based access: Admin for management, Users for reservations.

    Enable data-driven decisions with visual stats (e.g., spot availability, occupancy).

    Ensure system security with login/session controls and access restrictions.

🛠️ Technologies Used:

    Frontend: HTML, CSS, Bootstrap 5

    Backend: Python, Flask

    Templating: Jinja2

    Database: SQLite (via SQLAlchemy ORM)

    Authentication: Flask-Login (with role-based access)

👤 User Roles:
🔒 1. Admin:

    Access an exclusive dashboard with occupancy statistics.

    Add/manage parking lots.

    View registered users and their booking statistics.

    Access control ensures only admins can reach management routes.

👥 2. User:
    Register/login securely.

    View available parking lots.

    Book or release a parking slot.

    Access personal dashboard with booking history.

🔧 Functional Modules:
| Module              | Description                                                               |
| ------------------- | ------------------------------------------------------------------------- |
| User Authentication | Secure registration, login, and logout system.                            |
| Admin Dashboard     | Displays occupancy status of parking lots in graphical format.            |
| Parking Lot Mgmt    | Admins can create new lots and monitor space availability.                |
| User Dashboard      | Users can view their active bookings and available lots.                  |
| Booking System      | Book and release spots in real time (status updated dynamically).         |
| Flash Messaging     | Real-time feedback (e.g., errors, success alerts) using Bootstrap alerts. |
| Access Control      | Unauthorized access is restricted and redirected with proper messaging.   |
