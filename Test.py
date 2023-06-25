from flask import Flask, request,jsonify,session,json
import mysql.connector as sql
from twilio.rest import Client
import random



app = Flask(__name__)
conn = sql.Connect(host="127.0.0.1", user="root", password="samaan11", database="hayah0")
cursor = conn.cursor

array1={}
array2={}
array3={}

account_sid = 'ACc1ad6bd30c16cfacedad4464dd9bca12'
auth_token = 'b28656b4ae0dd485b41f9f2776e43645'
client = Client(account_sid, auth_token)

# Store the SMS codes in a dictionary
sms_codes = {}

@app.route('/generate_code', methods=['POST'])
def generate_code():
    # Collect the user's phone number from the request
    phone_number = request.json.get('phone')

    # Generate a unique code
    code = str(random.randint(1000, 9999))

    # Send the SMS code using the Twilio API
    message = client.messages.create(
        body=f'Your verification code is {code}',
        from_='+15855153830',
        to='20'+phone_number
    )

    # Store the code in the dictionary
    sms_codes[phone_number] = code

    # Return a success message to the client
    response = {'success': True, 'message': 'SMS code sent successfully.'}
    return jsonify(response),200



@app.route('/updateDonorInfo',methods =['POST'])
def updateDonor():
    if request.method =="POST"and 'id' in session:
        _id = session['id']
        address=request.form['address']
        city=request.form['city']
        phone=request.form['phone']
        password=request.form['password']
        code = request.json.get('code')
        full_address = address + city

        # Check if the phone number is in the dictionary
        if phone in sms_codes:
            # Check if the code matches the one in the dictionary
            if sms_codes[phone] == code:
                # Remove the code from the dictionary
                del sms_codes[phone]
                
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
        Doctor_Code = session['code']
        address=request.form['address']
        city=request.form['city']
        phone=request.form['phone']
        password=request.form['password']
        code = request.json.get('code')
        full_address = address + city

         # Check if the phone number is in the dictionary
        if phone in sms_codes:
            # Check if the code matches the one in the dictionary
            if sms_codes[phone] == code:
                # Remove the code from the dictionary
                del sms_codes[phone]


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
            cursor.execute("""SELECT * FROM `doctors` WHERE `DoctrosCode` = {}""".format(code))
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

@app.route('/Discount', methods = ['POST'])
def createDiscount():
    if request.method=='POST':
        if 'id' in session:
            with open(r'C:\Users\User\Desktop\alpha.jpg','rb') as file:
                blob_data = file.read()
            DataDic={}
            id = session['id']
            try:

                cursor.execute("""SELECT `num_of_times_donated` FROM `donors` WHERE `DonorID` LIKE '{}'""".format(id))
                numberOfTimesDonated= cursor.fetchone()
                if numberOfTimesDonated:
                    if(numberOfTimesDonated[9]>5):
                        cursor.execute("""INSERT INTO `discounts` (`percentage`, `LabName`,`DiscountNumber`,`discountImage`) VALUES ({}, {}, '{}', '{}', '{}',{},'{}')""".format(40,'alpha',5,blob_data))
                        
                        cursor.execute("""INSERT INTO `getting_offer` ( `Donor_IDDD`, `NumOfTimesDonated`) VALUES ({}, {}, '{}')""".format(id,numberOfTimesDonated))
                        cursor.execute("""SELECT `Discount_ID` FROM `getting_offer` WHERE `Donor_IDDD` = {} """.format(id))
                        DiscountID = cursor.fetchone()
                        cursor.execute("""SELECT * FROM `discounts` WHERE `DiscountID` = {}""".format(DiscountID))
                        DiscountData=cursor.fetchone()
                        conn.commit()
                        DataDic['DiscountID']=DiscountData[0]
                        DataDic['percentage']=DiscountData[1]
                        DataDic['LabName']=DiscountData[2]
                        DataDic['DiscountNumber']=DiscountData[3]
                        DataDic['DiscountImage']=DiscountData[4]

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

    
if __name__ == "__main__":

    app.run(debug=True)