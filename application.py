from flask import Flask, request,jsonify,session,json
import mysql.connector as sql
from twilio.rest import Client
import random
from passlib.hash import sha256_crypt
import re
import os
# importing datetime module for now()
import datetime
import base64


app = Flask(__name__)
conn = sql.Connect(host="127.0.0.1", user="root", password="samaan11", database="hayah0")
cursor = conn.cursor()
app.secret_key = os.urandom(24)

array1={}
array2={}
array3={}


account_sid = 'ACc1ad6bd30c16cfacedad4464dd9bca12'
auth_token = 'b28656b4ae0dd485b41f9f2776e43645'
client = Client(account_sid, auth_token)

# Store the SMS codes in a dictionary
sms_codes = {}
oldPhones = None
@app.route('/')
def index():
    return 'Hello from here'

import vonage

client = vonage.Client(key="e32ed317", secret="La8rDbRF5WYKAUPX")
sms = vonage.Sms(client)


@app.route('/send-sms', methods=['POST'])
def send_sms():
    # Get the recipient's phone number and the message content from the request
    phone_number = request.json.get('phone_number')
    print(phone_number)
    #message = request.form.get('message')
    fullPhoneNumber = '+2'+ str(phone_number)
    if not fullPhoneNumber:
        return jsonify({'message': 'Phone number is required'}), 400

    code = str(random.randint(1000, 9999))
    print(fullPhoneNumber)
    # Send the SMS using the Nexmo client
    response = sms.send_message({
        'from': 'hayah',  # Replace with your Nexmo virtual number or alphanumeric sender ID
        'to':fullPhoneNumber,
        'text': f'Your verification code is {code}    '
    })

    if response['messages'][0]['status'] == '0':
        return jsonify({'message':'SMS sent successfully'}),200
    else:
        return jsonify({'message':'SMS failed to send'}),400




@app.route("/register", methods=['Post'])
def register():
    global oldPhones
    fname = request.json.get('ufname')
    lname = request.json.get('ulname')
    email = request.json.get('uemail')
    password = request.json.get('upassword').encode()
    phone = request.json.get('uphone')
    gender = request.json.get('Gender')
    blood_type = request.json.get('blood_types')
    street = request.json.get('uAddress')
    age = request.json.get('uage')
    oldPhones = phone
    print(oldPhones)
    encrypted_password = sha256_crypt.encrypt(password)

    cursor.execute('SELECT * FROM donors WHERE Email = %s', (email,))
    account = cursor.fetchone()
    # If account exists show error and validation checks
    try:
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z]+', fname):
            msg = 'First Name must contain only characters !'
        elif not re.match(r'[A-Za-z]+', lname):
            msg = 'Last Name must contain only characters !'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute("""INSERT INTO `donors` (`FName`, `LName`, `Email`, `Dpassword`, `PhoneNumber`, 
                            `Gender`,`Blood_type`, `address`, `age`) VALUES 
                            ('{}', '{}', '{}', '{}', '{}','{}',
                            '{}', '{}', '{}')"""
                            .format(fname, lname, email, encrypted_password, phone, gender, blood_type, street, age))

            cursor.execute("""SELECT * FROM `Donors` WHERE `Email` LIKE '{}'""".format(email))
            account = cursor.fetchone()
            session['id'] = account[0]
            session['email'] = account[3]
            conn.commit()
            response = {'success': True, 'message': 'Registerd successfully.'}
            return jsonify(response),200
        return jsonify({'error': msg}), 400
    except Exception as e:
            return jsonify({'error': str(e)}),500
    

@app.route('/login_validation', methods = ['POST', 'GET'])
def login_validation():
    user = request.json.get('User')
    if user == "Donor":
        return donor_login_validation()
    elif user == "Doctor":
        return doctor_login_validation()
    else:
        return jsonify({'error': 'Invalid choice , Please Try again'}),403


@app.route('/donor_login_validation', methods=['POST', 'GET'])
def donor_login_validation():
    email = request.json.get('email')
    password = request.json.get('password')
    cursor.execute("""SELECT * FROM `Donors` WHERE `Email` = '{}'"""
                   .format(email))

    account = cursor.fetchone()
    user_hashed_password = account[4]

    if sha256_crypt.verify(password, user_hashed_password):
        session['logged'] = True
        session['id'] = account[0]
        session['email'] = account[3]
        response = {'success': True, 'message': 'Logged in successfully.'}
        return jsonify(response),200
    else:
        # Account doesnt exist or username/password incorrect
        msg = 'Incorrect username/password!'
        #print(msg)
        return jsonify({'success': False,'message':msg}),406


@app.route('/doctor_validation', methods=['POST', 'GET'])
def doctor_login_validation():
    email = request.json.get('email')

    password = request.json.get('password')
    cursor.execute("""SELECT * FROM `Doctors` WHERE `doctor_email` = '{}'"""
                   .format(email))

    account = cursor.fetchone()
    doctor_password = account[4]

    if password == doctor_password:
        session['logged'] = True
        session['code'] = account[0]
        session['email'] = account[3]
        response = {'success': True, 'message': 'Logged in successfully.'}
        return jsonify(response),200
    else:
        # Account doesnt exist or username/password incorrect
        msg = 'Incorrect username/password!'
        #print(msg)
        return jsonify({'success': False,'message':msg}),406

@app.route('/generate_code', methods=['POST'])
def generate_code():
    # Collect the user's phone number from the request
    phone_number = request.json.get('phone')

    # Generate a unique code
    code = str(random.randint(1000, 9999))

    # Send the SMS code using the Twilio API
    message = client.messages.create(
        body=f'Your verification code is {code}',
        from_='+12708183360',
        to='+2'+phone_number
    )

    # Store the code in the dictionary
    sms_codes[phone_number] = code

    # Return a success message to the client
    response = {'success': True, 'message': 'SMS code sent successfully.'}
    return jsonify(response),200



@app.route('/updateDonorInfo',methods =['POST'])
def updateDonor():
    if request.method =="POST"and 'id' in session:
        global oldPhones
        _id = session['id']
        address=request.json.get('address')
        city=request.json.get('city')
        phone=request.json.get('phone')
        password=request.json.get('password')
        code = request.json.get('code')
        full_address = address +' ' +city
        print(oldPhones)
        # Check if the phone number is in the dictionary
        if oldPhones in sms_codes:
            # Check if the code matches the one in the dictionary
            if sms_codes[oldPhones] == code:
                # Remove the code from the dictionary
                del sms_codes[oldPhones]
                
                cursor.execute("""UPDATE `Donors` SET `address` = '{}',  `PhoneNumber`  ={}, `Dpassword`  = '{}' WHERE `DonorID` ={} """.format(full_address,phone,password,_id))
                conn.commit()
                # Return a success message to the client
                response = {'success': True, 'message': 'SMS code verification successful.'}
                return jsonify(response), 200

        # If the phone number or code is incorrect, return an error message
        response = {'success': False, 'error': 'Invalid phone number or SMS code.'}
        return jsonify(response), 404
    else:
        return jsonify({'error': 'Not logged in:Unauthoriezed'}),401

        #return jsonify(["information update success"])
        #return""


@app.route('/updateDoctorInfo',methods =['POST'])
def updateDoctor():
    if request.method =="POST" and 'id' in session:
        global oldPhones
        Doctor_Code = session('code')
        address=request.json.get('address')
        city=request.json.get('city')
        phone=request.json.get('phone')
        password=request.json.get('password')
        code = request.json.get('code')
        full_address = address +' ' + city

         # Check if the phone number is in the dictionary
        if phone in sms_codes:
            # Check if the code matches the one in the dictionary
            if sms_codes[oldPhones] == code:
                # Remove the code from the dictionary
                del sms_codes[oldPhones]


                cursor.execute("""UPDATE `doctors` SET `doctor_address` = '{}', `Doctor_PhoneNumber`  ={} , `doctor_password`  ='{}' WHERE `DoctorsCode` ={} """.format(full_address,phone,password,Doctor_Code))
                conn.commit()
                # Return a success message to the client
                response = {'success': True, 'message': 'SMS code verification successful.'}
                return jsonify(response), 200
        # If the phone number or code is incorrect, return an error message
        response = {'success': False, 'error': 'Invalid phone number or SMS code.'}
        return jsonify(response), 404
        #return jsonify(["information update success"])
        #return""
    else:
        return jsonify({'error': 'Not logged in:Unauthoriezed'}),401

@app.route("/create_report", methods=['Post'])
def report():
    try:
        #doctor_code = request.form.get('doctor_code')
        #donor_email = request.form.get('donor_email')
        donor_id = session["id"]
        doctor_code = session['code']
        status = request.json.get('status')
        reason = request.json.get('reason')
        # using now() to get current time
        current_time = datetime.datetime.now()
        mchc = request.json.get('mchc')
        hba1c = request.json.get('hba1c')
        sgot_ast = request.json.get('sgot_ast')
        sgot_alt = request.json.get('sgot_alt')
        blood_urea = request.json.get('blood_urea')
        serum_creatine = request.json.get('serum_creatine')
        serum_uric_acid = request.json.get('serum_uric_acid')
        hemoglobine = request.json.get('hemo')
        red_cells_count = request.json.get('red_cells_count')
        mch = request.json.get('mch')
        mcv = request.json.get('mcv')
        platelet_count = request.json.get('platelet_count')
        HIV_Antibody = request.json.get('HIV_Antibody')
        HBs_Antigen = request.json.get('HBs_Antigen')
        HCV_Ab_lgG = request.json.get('HCV_Ab_lgG')
        vdrl = request.json.get('VDRL')

        #cursor.execute("""INSERT INTO `reports` (`status`,`reason`,`Report_Date_Time`,
        # `Hemoglobin_Concentration_Mean_Corpuscular_MCHC`, `Glycated_Hemoglobin_HBA1C`, 
        # `Serum_Aspartate_Transfrerase_SGOT_AST`, `Serum_Alanine_Transfrerase_SGPT_ALT`, 
        # `Blood_Urea_Niterogen_BUN`, `Serum_creatinine`, `Serum_uric_Acid`,
        # `Hemoglobin`, `Red_Blood_Cell_Count`, `MCH`, `MCV`, `Platelet_Count`,`HIV_Antibody`,`HBs_Antigen`,`HCV_Ab_lgG`,`VDRL`, `Donor_ID`, 
        # `Doctor_Code`) VALUES 
        # ({} ,{} ,{} ,{} ,{} ,{} ,{} ,{} ,{} ,{} ,{} ,{} ,{} ,{} )"""
        #             .format(status,reason,current_time,mchc, hba1c, sgot_ast, sgot_alt, blood_urea, serum_creatine, serum_uric_acid, hemoglobine,
        #                     red_cells_count, mch, mcv, platelet_count,HIV_Antibody,HBs_Antigen,HCV_Ab_lgG,vdrl, donor_id, doctor_code))

        cursor.execute("""
            INSERT INTO `reports` (
                `status`,
                `reason`,
                `Report_Date_Time`,
                `Hemoglobin_Concentration_Mean_Corpuscular_MCHC`,
                `Glycated_Hemoglobin_HBA1C`,
                `Serum_Aspartate_Transfrerase_SGOT_AST`,
                `Serum_Alanine_Transfrerase_SGPT_ALT`,
                `Blood_Urea_Niterogen_BUN`,
                `Serum_creatinine`,
                `Serum_uric_Acid`,
                `Hemoglobin`,
                `Red_Blood_Cell_Count`,
                `MCH`,
                `MCV`,
                `Platelet_Count`,
                `HIV_Antibody`,
                `HBs_Antigen`,
                `HCV_Ab_lgG`,
                `VDRL`,
                `Donor_ID`,
                `Doctor_Code`
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            status,
            reason,
            current_time,
            mchc,
            hba1c,
            sgot_ast,
            sgot_alt,
            blood_urea,
            serum_creatine,
            serum_uric_acid,
            hemoglobine,
            red_cells_count,
            mch,
            mcv,
            platelet_count,
            HIV_Antibody,
            HBs_Antigen,
            HCV_Ab_lgG,
            vdrl,
            donor_id,
            doctor_code
        ))

        #cursor.execute("""SELECT `num_of_times_donated` FROM `donors` WHERE `DonorID` LIKE '{}'""".format(donor_id))
        cursor.execute("""
            SELECT `num_of_times_donated`
            FROM `donors`
            WHERE `DonorID` = %s
        """, (donor_id,))
        numberOfTimesDonated= cursor.fetchone()
        if numberOfTimesDonated[0] is None:
            numberOfTimesDonated =1
        else:
            numberOfTimesDonated = numberOfTimesDonated[0] +1
        
        #cursor.execute("""UPDATE `Donors` SET `num_of_times_donated` = '{}' WHERE `DonorID` LIKE '{}'""".format(numberOfTimesDonated,donor_id))
        cursor.execute("""
            UPDATE `Donors`
            SET `num_of_times_donated` = %s
            WHERE `DonorID` = %s
        """, (numberOfTimesDonated, donor_id))
        conn.commit()
        response = {'success': True, 'message': 'A new report generated!.'}
        return  jsonify(response),200
    except Exception as e:
            return jsonify({'error': str(e)}),401
  
@app.route('/GetReportID', methods = ['GET'])
def getID():
    if 'id' in session:
        id = session['id']
        try:
            cursor.execute("""SELECT `ReportID` FROM `reports` WHERE `Donor_ID` = {} ORDER BY `Report_Date_Time` DESC""".format(id))
            reportsID=cursor.fetchall()
            if reportsID:
                reportsIDList= [item for t in reportsID for item in t]
                return jsonify(reportsIDList), 200
            else:
                return jsonify({'error': 'Reports ID not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}),500
    else:
        return jsonify({'error': 'Not logged in:Unauthoriezed'}),401
        

@app.route('/GetReportInfo/<int:ReportID>', methods = ['GET'])
def getReport(ReportID):
    if 'id' in session:
        id = session['id']
        try:
            cursor.execute("""SELECT * FROM `reports` WHERE `Donor_ID` = {} AND `ReportID` = {}""".format(id,ReportID))
            report = cursor.fetchone()
            if report:
                array1['Doctor_Code']=report[21]
                array1['ReportID']=report[0]
                array1['Blood_ID']=report[22]
                array1['ReportDate']=report[3]
                array1['Hemoglobin']=report[15]
                array1['RedBloodCellCount']=report[16]
                array1['MCH']=report[17]
                array1['MCV']=report[18]
                array1['MCHC']=report[4]
                array1['PlateletCount']=report[19]
                array1['HBA1c']=report[5]
                array1['SGOT_ASAT']=report[6]
                array1['SGPT_ALT']=report[7]
                array1['BloodUrea']=report[8]
                array1['SerumCreatinine']=report[9]
                array1['SerumUricAcid']=report[10]
                array1['reason']=report[2]
                array1['status']=report[1]
                array1['HIV_Antibody']=report[11]
                array1['HBs_Antigen']=report[12]
                array1['HCV_Ab_lgG']=report[13]
                array1['VDRL']=report[14]

                #print("GetReportInfo")
                return jsonify(array1),200
            else:
                return jsonify({'error': 'Report not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}),500
    else:
        return jsonify({'error': 'Not logged in:Unauthoriezed'}),401
    
@app.route('/GetDonorAccountInfo', methods = ['GET'])
def getDonorInfo():
    if 'id' in session:
        try:
            id = session['id']
            cursor.execute("""SELECT * FROM `donors` WHERE `DonorID` = {}""".format(id))
            AccountInfo = cursor.fetchone()
            if AccountInfo:
                array2['FName']=AccountInfo[1]
                array2['LName']=AccountInfo[2]
                array2['Email']=AccountInfo[3]
                array2['Blood_type']=AccountInfo[7]
                array2['address']=AccountInfo[8]
                array2['PhoneNumber']=AccountInfo[5]
                array2['age']=AccountInfo[10]
                array2['Gender']=AccountInfo[6]
                return jsonify(array2),200
            else:
                return jsonify({'error': 'Account not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}),500
    else:
        return jsonify({'error': 'Not logged in:Unauthoriezed'}),401


@app.route('/GetDoctorAccountInfo', methods = ['GET'])
def getDoctorInfo():
    if 'code' in session:
        try:

            code = session['code']
            cursor.execute("""SELECT * FROM `doctors` WHERE `DoctorsCode` = {}""".format(code))
            AccountInfo = cursor.fetchone()
            if AccountInfo:

                array3['FName']=AccountInfo[1]
                array3['LName']=AccountInfo[2]
                array3['doctor_email']=AccountInfo[3]
                array3['doctor_address']=AccountInfo[6]
                array3['doctor_phonenumber']=AccountInfo[5]
                array3['Center_ID']=AccountInfo[7]

                return jsonify(array3),200
            else:
                return jsonify({'error': 'Doctor Account not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}),500
    else:
        return jsonify({'error': 'Not logged in:Unauthoriezed'}),401    

imageData =None
@app.route('/CreateDiscount', methods = ['POST'])
def createDiscount():
    if request.method=='POST':
        if 'id' in session:
            with open(r'D:\fcis\GP\New folder\Task1\static\alpha.jpg','rb') as file:
                blob_data = file.read()
            global imageData    
            imageData=blob_data
            DataDic={}
            id = session['id']
            try:

                cursor.execute("""SELECT `num_of_times_donated` FROM `donors` WHERE `DonorID` = {}""".format(id))
                numberOfTimesDonated= cursor.fetchone()
                if numberOfTimesDonated:
                    if(numberOfTimesDonated[0]>5):
                        NewnumberOfTimesDonated = numberOfTimesDonated[0]
                        #cursor.execute("""INSERT INTO `discounts` (`percentage`, `LabName`,`DiscountNumber`,`discountImage`) VALUES ({}, '{}', {},'{}')""".format(40,'alpha',5,blob_data))
                        cursor.execute("""INSERT INTO `discounts` (`percentage`, `LabName`, `DiscountNumber`, `discount_image`) VALUES (%s, %s, %s, %s)""", (40, 'alpha', 5, blob_data))
                        conn.commit()  # Commit the insert into discounts
                        discount_id = cursor.lastrowid  # Get the auto-incremented DiscountID
                        cursor.execute("""INSERT INTO `getting_offer` ( `Discount_ID`,`Donor_IDDD`, `NumOfTimesDonated`) VALUES ({},{}, {})""".format(discount_id,id,NewnumberOfTimesDonated))
                        conn.commit()  # Commit the insert into discounts-
                        DataDic= {'success':True, 'message':'A new Discount has been created !'}
                        return jsonify(DataDic), 200
                    else:
                        response = {'success': False, 'error': 'This donor does not have any discounts'}
                        return jsonify(response),404
                else:
                    return jsonify({'error': 'This donor does not have any discounts'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}),500

        else:
            return jsonify({'error': 'Not logged in:Unauthoriezed'}),401
    else:
        return jsonify({'error': 'This method is not allowed'}),405

@app.route('/getDiscountImage', methods = ['GET'])
def image():
    if request.method=='GET':
        if 'id' in session:
            id = session['id']
            DataDic={}
            global imageData
            try:
                cursor.execute("""SELECT `num_of_times_donated` FROM `donors` WHERE `DonorID` = {}""".format(id))
                numberOfTimesDonated= cursor.fetchone()
                if numberOfTimesDonated:
                    if(numberOfTimesDonated[0]>5):
                        # cursor.execute("""SELECT `Discount_ID` FROM `getting_offer` WHERE `Donor_IDDD` = {} """.format(id))                
                        # DiscountID = cursor.fetchone()
                        # #cursor.execute("""SELECT * FROM `discounts` WHERE `DiscountID` = {}""".format(DiscountID))
                        # cursor.execute("""SELECT * FROM `discounts` WHERE `DiscountID` = %s""", (DiscountID[0],))
                        # DiscountData=cursor.fetchone()
                        print(imageData)
                        DataDic['DiscountImage']=base64.b64encode(imageData).decode('utf-8')  # Convert to Base64 string
                        return jsonify(DataDic), 200
                    else:
                        response = {'success': False, 'error': 'This donor does not have any discounts'}
                        return jsonify(response),404
                else:
                    return jsonify({'error': 'This donor does not have any discounts'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}),500
        else:
            return jsonify({'error': 'Not logged in:Unauthoriezed'}),401
    else:
        return jsonify({'error': 'This method is not allowed'}),405        

@app.route('/getDiscountData/<int:DiscountID>', methods = ['GET'])
def GetDiscount(DiscountID):
    if request.method=='GET':
        if 'id' in session:
            id = session['id']
            DataDic={}
            try:
                cursor.execute("""SELECT `num_of_times_donated` FROM `donors` WHERE `DonorID` = {}""".format(id))
                numberOfTimesDonated= cursor.fetchone()
                if numberOfTimesDonated:
                    if(numberOfTimesDonated[0]>5):
                        # cursor.execute("""SELECT `Discount_ID` FROM `getting_offer` WHERE `Donor_IDDD` = {} """.format(id))                
                        # DiscountID = cursor.fetchone()
                        #cursor.execute("""SELECT * FROM `discounts` WHERE `DiscountID` = {}""".format(DiscountID))
                        cursor.execute("""SELECT * FROM `discounts` WHERE `DiscountID` = %s""", (DiscountID,))
                        DiscountData=cursor.fetchone()
                        DataDic['DiscountID']=DiscountData[0]
                        DataDic['percentage']=DiscountData[1]
                        DataDic['LabName']=DiscountData[2]
                        DataDic['DiscountNumber']=DiscountData[3]
                        return jsonify(DataDic), 200
                    else:
                        response = {'success': False, 'error': 'This donor does not have any discounts'}
                        return jsonify(response),404
                else:
                    return jsonify({'error': 'This donor does not have any discounts'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}),500
        else:
            return jsonify({'error': 'Not logged in:Unauthoriezed'}),401
    else:
        return jsonify({'error': 'This method is not allowed'}),405        

@app.route('/getDiscountNotificationID', methods = ['GET'])
def GetDiscountNotification():
    if request.method=='GET':
        if 'id' in session:
            id = session['id']
            try:
                cursor.execute("""SELECT `num_of_times_donated` FROM `donors` WHERE `DonorID` = {}""".format(id))
                numberOfTimesDonated= cursor.fetchone()
                if numberOfTimesDonated:
                    if(numberOfTimesDonated[0]>5):
                        cursor.execute("""SELECT `Discount_ID` FROM `getting_offer` WHERE `Donor_IDDD` = {} ORDER BY `Discount_ID` DESC """.format(id))                
                        DiscountsID = cursor.fetchall()
                        #cursor.execute("""SELECT * FROM `discounts` WHERE `DiscountID` = {}""".format(DiscountID))
                        #cursor.execute("""SELECT * FROM `discounts` WHERE `DiscountID` = %s""", (DiscountID[0],))
                        #DiscountData=cursor.fetchone()
                        # DataDic['DiscountID']=DiscountData[0]
                        # DataDic['percentage']=DiscountData[1]
                        # DataDic['LabName']=DiscountData[2]
                        # DataDic['DiscountNumber']=DiscountData[3]
                        if DiscountsID:
                            DiscountsIDList= [item for t in DiscountsID for item in t]
                            return jsonify(DiscountsIDList), 200
                        else:
                            return jsonify({'error': 'Discount ID not found'}), 404
                        
                    else:
                        response = {'success': False, 'error': 'This donor does not have any discounts'}
                        return jsonify(response),404
                else:
                    return jsonify({'error': 'This donor does not have any discounts'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}),500
        else:
            return jsonify({'error': 'Not logged in:Unauthoriezed'}),401
    else:
        return jsonify({'error': 'This method is not allowed'}),405        




if __name__ == "__main__":

    app.run(debug=True)