from flask import Blueprint, flash, render_template, redirect, request, url_for
from .models import db, ParkingLot, ParkingSpot, Booking, User
from datetime import datetime
from flask_login import fresh_login_required, login_required, current_user
from sqlalchemy import Float

# home 
views = Blueprint('views', __name__)
@views.route('/')
def home():
    return redirect('/login')

#register user route
@views.route('/admin/users', methods=['GET', 'POST'])
@login_required
def view_users():
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for('views.user_dashboard'))

    users = User.query.filter_by(is_admin=False).all()
    return render_template('view_users.html', users=users)


#admin dashboard route
@views.route('/admin/dashboard')
@fresh_login_required
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('views.user_dashboard'))

    lots = ParkingLot.query.all()
    users = User.query.filter_by(is_admin=False).all()

    stats = []
    for lot in lots:
        total = len(lot.spots)
        occupied = sum(1 for spot in lot.spots if spot.status == 'Occupied')
        available = total - occupied
        stats.append({'location': lot.location, 'occupied': occupied, 'available': available})


    return render_template("admin_dashboard.html", lots=lots, stats=stats, users=users)

# add lot route
@views.route('/add_lot', methods=['GET', 'POST'])
@login_required
def add_lot():
    if not current_user.is_admin:
        flash("Access denied")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        location = request.form.get('location')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        price  = float(request.form.get('price'))
        max_spots = int(request.form.get('max_spots'))

        new_lot = ParkingLot(

            location = location,
            address = address,
            pincode = pincode,
            price = price,
            max_spots = max_spots
        )
        db.session.add(new_lot)
        db.session.commit()


        for i in range(new_lot.max_spots):
            spot = ParkingSpot(lot=new_lot, spot_number=i+1, is_occupied=False)

            db.session.add(spot)
        db.session.commit()
        flash("parkinglot and spots added successfully!")
        return redirect('/admin/dashboard')
    return render_template('add_lot.html')

# user dashboard route
@views.route('/user_dashboard', methods=['GET', 'POST'])
@fresh_login_required
@login_required
def user_dashboard():
    lots = ParkingLot.query.all()  

    if request.method == 'POST':
        selected_lot_id = request.form.get('lot_id')
        lot = ParkingLot.query.get(selected_lot_id)

        spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()
        if not spot:
            flash("No available spots in this lot.")
            return redirect('/user_dashboard')

        spot.status = 'Occupied'
        db.session.add(spot)

        booking = Booking(
            user_id=current_user.id,
            spot_id=spot.id,
            start_time=datetime.utcnow()
        )
        db.session.add(booking)
        db.session.commit()

        flash(f"Spot booked in {lot.location}!")
        return redirect('/user_dashboard')

    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('user_dashboard.html', lots=lots, bookings=bookings)

#realease booking route
@views.route('/book/<int:lot_id>', methods=['POST'])
@login_required
def book_spot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    available_spot = ParkingSpot.query.filter_by(lot_id=lot.id, is_occupied=False).first()

    if not available_spot:
        flash("No available spots in this lot.", "danger")
        return redirect(url_for('views.user_dashboard'))

    available_spot.is_occupied = True

    booking = Booking(
        user_id=current_user.id,
        lot_id=lot.id,
        spot_id=available_spot.id,
        start_time=datetime.now(),
        is_active=True
    )

    db.session.add(booking)
    db.session.commit()

    flash("Spot booked successfully!", "success")
    return redirect(url_for('views.user_dashboard'))

#cost calculation route 
@views.route('/release/<int:booking_id>')
@login_required
def release_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id or not booking.is_active:
        flash("Invalid operation.", "danger")
        return redirect(url_for('views.user_dashboard'))

    end_time = datetime.now()
    duration_hours = (end_time - booking.start_time).total_seconds() / 3600
    duration_hours = max(duration_hours, 0.01)

    price_per_hour = booking.spot.lot.price
    total_cost = round(duration_hours * price_per_hour, 2)

    booking.end_time = end_time
    booking.cost = total_cost
    booking.is_active = False

    booking.spot.is_occupied = False

    db.session.commit()

    flash(f"Your spot has been released and your total cost is: Rs {total_cost}", "info")
    return redirect(url_for('views.user_dashboard'))

# edit lot route

@views.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.location = request.form['location']
        lot.address = request.form['address']
        lot.pincode = request.form['pincode']
        lot.price = float(request.form['price'])

        # Update max spots and sync the ParkingSpot table
        new_max_spots = int(request.form['max_spots'])
        current_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        current_count = len(current_spots)

        lot.max_spots = new_max_spots

        if new_max_spots > current_count:
            # Assign spot_number starting from the max existing one + 1
            existing_spot_numbers = [
                spot.spot_number for spot in current_spots if spot.spot_number is not None
            ]
            next_spot_number = max(existing_spot_numbers, default=0) + 1

            for i in range(new_max_spots - current_count):
                new_spot = ParkingSpot(
                    lot_id=lot.id,
                    status='A',
                    is_occupied=False,
                    spot_number=next_spot_number + i
                )
                db.session.add(new_spot)

        elif new_max_spots < current_count:
            # Remove unoccupied spots first
            available_spots = ParkingSpot.query.filter_by(
                lot_id=lot.id, status='A', is_occupied=False
            ).limit(current_count - new_max_spots).all()

            for spot in available_spots:
                db.session.delete(spot)

            if len(available_spots) < (current_count - new_max_spots):
                flash("Some spots are currently occupied and can't be removed.", "warning")

        db.session.commit()
        flash('Lot and spot info updated successfully!', 'success')
        return redirect('/admin/dashboard')

    return render_template('edit_lot.html', lot=lot)



#  Delete Lot Route
@views.route('/delete_lot/<int:lot_id>', methods=['GET', 'POST'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    # delete its spots and bookings
    for spot in lot.spots:
        Booking.query.filter_by(spot_id=spot.id).delete()
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()
    flash('Lot deleted successfully!')
    return redirect('/admin/dashboard')
