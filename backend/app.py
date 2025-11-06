from sys import exception
from flask import Flask,request,jsonify
from flask_cors import CORS
import bcrypt
import psycopg2
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os
from psycopg2.extras import RealDictCursor
import jwt
from helper.generate_token import generate_refresh_token,decode_token,generate_access_token
import requests

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv("FLASK_SECRET_KEY","THE_SECRET_KEY")



def database_connection():
    try:
        return psycopg2.connect(
            host = os.getenv('DB_HOST','localhost'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            database = os.getenv('DB_NAME')
        )
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        raise
    
    

def get_cookie_settings():
    is_local = ("localhost" in request.host) or ("127.0.0.1" in request.host)
    secure_cookie = False if is_local else True
    samesite_cookie = "Lax" if is_local else "None"  
    domain_cookie = None  
    return secure_cookie, samesite_cookie, domain_cookie    
    
@app.route('/signup',methods=['POST'])
def signup():
    if not request.is_json:
        return jsonify({"message":"Request must be jsonify","status":"error","user":None}),400

    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirmpassword = data.get('confirmpassword')
    
    if not all ([firstname,lastname,email,username,password,confirmpassword]):
        return jsonify({"message":"All fields are required"}),400
    if password != confirmpassword:
        return jsonify({"message":"Passwords do not match"}),400
    if len(password) < 6:
        return jsonify({"message":"Length of Password must be more than 6"}),400
    try:
        
        hashpassword = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("select email from loginusers where email = %s",(email,))
        if cursor.fetchone():
            return jsonify({"message":"Email already exists","status":"error","user":None}),409
        
        cursor.execute("select username from loginusers where username = %s",(username,))
        if cursor.fetchone():
            return jsonify({"message":"Username already exists","status":"error","user":None}),409
        
        cursor.execute("insert into loginusers(firstname,lastname,email,username,passwords) values (%s,%s,%s,%s,%s)",
        (firstname,lastname,email,username,hashpassword)
        )
        db.commit()
        
        access_token = generate_access_token(email,role='guest')
        refresh_token = generate_refresh_token(email,role='guest')
        secure_cookie,samesite_cookie,domain_cookie = get_cookie_settings()
        guest = {"firstname":firstname,"lastname":lastname,"email":email}
        response = jsonify({"message":"Signup succesfull",
                            "status":"succes",
                            "user":guest}) 
        
    
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=secure_cookie,
            samesite=samesite_cookie,
            domain=domain_cookie,
            max_age=7*24*60*60
        )
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=secure_cookie,
            samesite=samesite_cookie,
            domain=domain_cookie,
            max_age=15*60
        )
        
        return response,200
    except psycopg2.Error as e:
        return jsonify({"message":"Database error","error":str(e),"status":"error","user":None}),500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()
            
            
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all ([username,password]):
        return jsonify({"message":"Both username and password required"}),400
    
    try:
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor) 
        cursor.execute("select passwords,role,email,username,firstname,lastname from loginusers where username = %s",(username,))           
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"message":"User Account not found"}),404
        
        passwords = user['passwords'].encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'),passwords):
            return jsonify({"message":"Incorrect passwords"}),404
        
        role = user.get('role','guest')
        email = user['email']
        
        if role != 'guest':
            return jsonify({"message":"Login unsuccessfull,only for guest"}),403
        
        access_token = generate_access_token(email,role)
        refresh_token = generate_refresh_token(email,role)
        secure_cookie,samesite_cookie,domain_cookie = get_cookie_settings()
        
        response = jsonify({"message":"Login successful",
                            "status":"success",
                            "access_token":access_token,
                            "user":{
                                "username":user['username'],
                                "email":user["email"],
                                "role":role,
                                "firstname":user.get("firstname"),
                                "lastname":user.get("lastname")
                                }
                            })
        response.set_cookie('refresh_token',refresh_token,
                            httponly=True,
                            secure=secure_cookie,
                            samesite=samesite_cookie,
                            domain=domain_cookie,
                            max_age=7*24*60*60,
                            path='/'    
                            )
        
        response.set_cookie('access_token',access_token,
                            httponly=True,
                            secure=secure_cookie,
                            samesite=samesite_cookie,
                            domain=domain_cookie,
                            max_age=15*60,
                            path='/'
                            )
        
        return response,200
    except psycopg2.Error as e:
        return jsonify({"message":"Something Happened,Connection Error","error":str(e)}),500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()


@app.route('/adminlogin', methods=['POST'])
def adminlogin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not all([email,password]):
        return jsonify({"message":"Email and Password required"}),400
    
    try:
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute("select passwords,email,role,username,firstname,lastname from loginusers where email = %s",(email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"message":"Account not found"}),404
        
        passwords = user['passwords'].encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'),passwords):
            return jsonify({"message":"Incorrect Password"}),404
        
        role = user.get('role','admin')
        email = user['email']
        
        if role != 'admin':
            return jsonify({"message":"Login unsuccessfull,Unauthoised Account"}),403
        
        access_token = generate_access_token(email,role)
        refresh_token = generate_refresh_token(email,role)
        secure_cookie,samesite_cookie,domain_cookie = get_cookie_settings()        
        
        response =  jsonify({"message":"Login Successfull",
                             "status":"success",
                             "access_token":access_token,
                             "user":{
                                 "username":user.get("username"),
                                 "email":user["email"],
                                 "role":role,
                                 "firstname":user.get("firstname"),
                                 "lastname":user.get("lastname")
                                 }
                             })
        
        response.set_cookie('refresh_token',refresh_token,
                            httponly=True,
                            secure=secure_cookie,
                            samesite=samesite_cookie,
                            domain=domain_cookie,
                            max_age=7*24*60*60,
                            path='/'
                            )
        
        response.set_cookie('access_token',access_token,
                            httponly=True,
                            secure=secure_cookie,
                            samesite=samesite_cookie,
                            domain=domain_cookie,
                            max_age=15*60,
                            path='/'
                            )
        
        return response,200
    except psycopg2.Error as e:
        return jsonify({"message":"Something Happened,Connection Error","error":str(e)}),500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()
            
            
@app.route('/superadmin', methods=['POST'])
def superadmin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not all ([email,password]):
        return jsonify({"message":"Email and Password required"}),400
    
    try:
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute("select passwords,username,role,email,firstname,lastname from loginusers where email = %s",(email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"message":"Account not Found"}),404
        
        passwords = user['passwords'].encode('utf-8') if isinstance(user['passwords'],str) else user['passwords']
        
        if not bcrypt.checkpw(password.encode('utf-8'),passwords):
            return jsonify({"message":"Incorrect Password"}),404
        
        role = user.get('role','superadmin')
        
        if role != 'superadmin':
            return jsonify({"message":"Unauthorised Access"}),403
        
        
        access_token = generate_access_token(email,role)
        refresh_token = generate_refresh_token(email,role)
        secure_cookie,samesite_cookie,domain_cookie = get_cookie_settings()
        
        response = jsonify({"message":"Login successful",
                            "status":"success",
                            "access_token":access_token,
                            "user":{
                                "username":user['username'],
                                "email":user["email"],
                                "role":role,
                                "firstname":user.get("firstname"),
                                "lastname":user.get("lastname")
                                }
                            })
        response.set_cookie('refresh_token',refresh_token,
                            httponly=True,
                            secure=secure_cookie,
                            samesite=samesite_cookie,
                            domain=domain_cookie,
                            max_age=7*24*60*60,
                            path='/'    
                            )
        
        response.set_cookie('access_token',access_token,
                            httponly=True,
                            secure=secure_cookie,
                            samesite=samesite_cookie,
                            domain=domain_cookie,
                            max_age=15*60,
                            path='/'
                            )
        
        
        return response,200             
    except psycopg2.Error as e:
        return jsonify({"message":"Something Happened,Connection Error","error":str(e)}),500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()
            
         
@app.route('/stafflogin', methods=['POST'])
def stafflogin():
    data = request.get_json()
    email = data.get('email') 
    password = data.get('password') 
    
    if not all ([email,password]) :
        return jsonify({"message":"Email and Password required"}),400
    
    try:
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute("select email,passwords,username,role,firstname,lastname from loginusers where email = %s",(email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"message":"Account not Found"}),404
        
        passwords = user['passwords'].encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'),passwords):
            return jsonify({"message":"Incorrect Password"}),404
        
        role = user.get('role','staff')
        email = user['email']
        
        if role != 'staff':
            return jsonify({"message":"Unauthorised"}),403
        
        access_token = generate_access_token(email,role)
        refresh_token = generate_refresh_token(email,role)
        secure_cookie,samesite_cookie,domain_cookie = get_cookie_settings()        
            
        response =  jsonify({"message":"Login Successfull",
                                "status":"success",
                                "access_token":access_token,
                                "user":{
                                    "username":user.get("username"),
                                    "email":user["email"],
                                    "role":role,
                                    "firstname":user.get("firstname"),
                                    "lastname":user.get("lastname")
                                    }
                                })
        
        response.set_cookie('refresh_token',refresh_token,
                            httponly=True,
                            secure=secure_cookie,
                            samesite=samesite_cookie,
                            domain=domain_cookie,
                            max_age=7*24*60*60,
                            path='/'
                            )
        
        response.set_cookie('access_token',access_token,
                            httponly=True,
                            secure=secure_cookie,
                            samesite=samesite_cookie,
                            domain=domain_cookie,
                            max_age=15*60,
                            path='/'
                            )
        
        return response,200    
    except psycopg2.Error as e:
        return jsonify({"message":"Something Happened,Connection Error","error":str(e)}),500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()
            

@app.route('/me', methods=['GET'])
def get_current_user():
    access_token = request.cookies.get('access_token')
    
    if not access_token:
        return jsonify({"message": "No token provided", "user": None}), 401
    
    try:
        payload = decode_token(access_token, is_refresh=False)
        if not payload:
            return jsonify({"message": "Invalid token", "user": None}), 401
        
        email = payload.get('email')
        role = payload.get('role', 'guest')
        
        
        try:
            db = database_connection()
            cursor = db.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT firstname, lastname, username, email, role FROM loginusers WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({"message": "User not found", "user": None}), 404
            
            return jsonify({
                "message": "User found",
                "user": {
                    "firstname": user.get('firstname'),
                    "lastname": user.get('lastname'),
                    "username": user.get('username'),
                    "email": user['email'],
                    "role": user.get('role', 'guest')
                }
            }), 200
        except psycopg2.Error as db_error:
            
            return jsonify({
                "message": "User found (from token)",
                "user": {
                    "email": email,
                    "role": role,
                    "firstname": "User",
                    "lastname": "",
                    "username": email.split('@')[0]
                }
            }), 200
        
    except Exception as e:
        return jsonify({"message": "Token validation failed", "error": str(e), "user": None}), 401
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()


@app.route('/refresh', methods=['POST'])
def refresh_token():
    refresh_token = request.cookies.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"message": "No refresh token provided"}), 401
    
    try:
        payload = decode_token(refresh_token, is_refresh=True)
        if not payload:
            return jsonify({"message": "Invalid refresh token"}), 401
        
        email = payload.get('email')
        role = payload.get('role', 'guest')
        
        
        new_access_token = generate_access_token(email, role)
        secure_cookie, samesite_cookie, domain_cookie = get_cookie_settings()
        
        response = jsonify({"message": "Token refreshed", "access_token": new_access_token})
        response.set_cookie(
            'access_token',
            new_access_token,
            httponly=True,
            secure=secure_cookie,
            samesite=samesite_cookie,
            domain=domain_cookie,
            max_age=15*60,
            path='/'
        )
        
        return response, 200
        
    except Exception as e:
        return jsonify({"message": "Token refresh failed", "error": str(e)}), 401


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"message": "Server is running", "status": "success"}), 200


@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Logged out", "status": "success"})
    response.set_cookie('refresh_token', '', expires=0, path='/')
    response.set_cookie('access_token', '', expires=0, path='/')
    return response, 200

            
@app.route('/hotel_booking', methods=['POST'])
def hotel_booking():
    access_token = request.cookies.get('access_token')
    if not access_token:
        return jsonify({"message": "No access token provided"}), 401    

    decoded = decode_token(access_token)
    if not decoded:
        return jsonify({"message":"Invalid or expired token"}),401

    user_email = decoded.get('email')
    if not user_email:
        return jsonify({"message":"Invalid Data"}),401
 
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    room_type = data.get('room_type')
    people = data.get('people')
    check_in = data.get('check_in')
    duration = data.get('duration')

    if not all([first_name, last_name, email, phone, room_type, people, check_in, duration]):
        return jsonify({"message": "All fields are required"}), 400

    try:
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        
        query = """
            INSERT INTO bookings 
            (first_name, last_name, email, phone, room_type, people, check_in, duration, status, user_email)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s)
            RETURNING id, check_in + (duration || ' days')::interval as check_out
        """
        cursor.execute(query, (
            first_name, last_name, email, phone, room_type, people, 
            check_in, duration, user_email
        ))
        
        booking = cursor.fetchone()
        db.commit()
        
        return jsonify({
            "message": "Booking created successfully",
            "booking_id": booking['id'],
            "check_out": booking['check_out'].strftime('%Y-%m-%d')
        }), 201
        
    except Exception as e:
        db.rollback()
        print(f"Error creating booking: {str(e)}")
        return jsonify({"message": "Failed to create booking"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()


@app.route('/admin/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    # Verify admin access
    access_token = request.cookies.get('access_token')
    if not access_token:
        return jsonify({"message": "No access token provided"}), 401
        
    decoded = decode_token(access_token)
    if not decoded or decoded.get('role') != 'admin':
        return jsonify({"message": "Unauthorized access"}), 403

    try:
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Get total bookings count
        cursor.execute("""
            SELECT COUNT(*) as total_bookings,
                   SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_bookings,
                   SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_bookings
            FROM bookings
        """)
        booking_stats = cursor.fetchone()
        
        # Get active guests count (bookings that are currently active)
        cursor.execute("""
            SELECT COUNT(DISTINCT email) as active_guests
            FROM bookings
            WHERE check_in <= CURRENT_DATE 
            AND (check_in + (duration || ' days')::interval) >= CURRENT_DATE
            AND status = 'confirmed'
        """)
        guest_stats = cursor.fetchone()
        
        
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM rooms WHERE status = 'available') as available_rooms,
                (SELECT COUNT(*) FROM rooms) as total_rooms
        """)
        room_stats = cursor.fetchone()
        
        return jsonify({
            "totalBookings": booking_stats['total_bookings'],
            "confirmedBookings": booking_stats['confirmed_bookings'],
            "pendingBookings": booking_stats['pending_bookings'],
            "activeGuests": guest_stats['active_guests'],
            "availableRooms": room_stats['available_rooms'],
            "totalRooms": room_stats['total_rooms']
        })
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {str(e)}")
        return jsonify({"message": "Failed to fetch dashboard stats"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

@app.route('/admin/bookings', methods=['GET'])
def get_all_bookings():
    
    access_token = request.cookies.get('access_token')
    if not access_token:
        return jsonify({"message": "No access token provided"}), 401
        
    decoded = decode_token(access_token)
    if not decoded or decoded.get('role') != 'admin':
        return jsonify({"message": "Unauthorized access"}), 403
        
    try:
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        
        cursor.execute("""
            SELECT 
                b.id, 
                b.first_name || ' ' || b.last_name as guest_name,
                b.email,
                b.phone,
                b.room_type,
                b.people,
                b.check_in,
                b.duration,
                (b.check_in + (b.duration || ' days')::interval)::date as check_out,
                b.status,
                b.created_at
            FROM bookings b
            ORDER BY b.created_at DESC
            LIMIT 10  # Return only the 10 most recent bookings for the dashboard
        """)
        
        bookings = cursor.fetchall()
        
        
        for booking in bookings:
            booking['check_in'] = booking['check_in'].strftime('%Y-%m-%d')
            booking['check_out'] = booking['check_out'].strftime('%Y-%m-%d')
            booking['created_at'] = booking['created_at'].isoformat()
        
        return jsonify(bookings)
        
    except Exception as e:
        print(f"Error fetching bookings: {str(e)}")
        return jsonify({"message": "Failed to fetch bookings"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

@app.route('/admin/bookings/<int:booking_id>/status', methods=['PUT'])
def update_booking_status(booking_id):
    # Verify admin access
    access_token = request.cookies.get('access_token')
    if not access_token:
        return jsonify({"message": "No access token provided"}), 401
        
    decoded = decode_token(access_token)
    if not decoded or decoded.get('role') != 'admin':
        return jsonify({"message": "Unauthorized access"}), 403
        
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status or new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
        return jsonify({"message": "Invalid status provided"}), 400
        
    try:
        db = database_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        
        cursor.execute("""
            UPDATE bookings 
            SET status = %s 
            WHERE id = %s
            RETURNING id, status
        """, (new_status, booking_id))
        
        updated_booking = cursor.fetchone()
        
        if not updated_booking:
            return jsonify({"message": "Booking not found"}), 404
            
        db.commit()
        
        return jsonify({
            "message": "Booking status updated successfully",
            "booking_id": updated_booking['id'],
            "new_status": updated_booking['status']
        })
        
    except Exception as e:
        db.rollback()
        print(f"Error updating booking status: {str(e)}")
        return jsonify({"message": "Failed to update booking status"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

if __name__ == '__main__':
    app.run(debug=True)
