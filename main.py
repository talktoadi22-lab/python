import csv
import os
from datetime import datetime
import pandas as pd

PATIENTS = "patients.csv"
APPOINTMENTS = "appointments.csv"

class Patient:
    def __init__(self, pid, name, age):
        self.pid, self.name, self.age = pid, name, age

class Appointment:
    def __init__(self, aid, pid, doctor, date):
        self.aid, self.pid, self.doctor, self.date = aid, pid, doctor, date
        self.arrival, self.start, self.waiting = "", "", ""
        self.status = "Booked"

def load(file):
    if not os.path.exists(file):
        headers = (["id", "name", "age"] if file == PATIENTS else
                   ["appointment_id", "patient_id", "doctor", "date",
                    "arrival", "start", "status", "waiting"])
        with open(file, "w", newline="") as f:
            csv.writer(f).writerow(headers)
    with open(file, newline="") as f:
        return list(csv.DictReader(f))

def save(file, rows):
    fields = (["id", "name", "age"] if file == PATIENTS else
              ["appointment_id", "patient_id", "doctor", "date",
               "arrival", "start", "status", "waiting"])
    with open(file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def register_patient():
    patients = load(PATIENTS)
    pid = "P" + str(len(patients) + 1).zfill(3)
    name = input("Patient name: ")
    age = input("Patient age: ")
    person = Patient(pid, name, age)
    patients.append({"id": person.pid, "name": person.name, "age": person.age})
    save(PATIENTS, patients)
    print("Patient registered. ID:", pid)

def view_patients():
    patients = load(PATIENTS)
    print(pd.DataFrame(patients).to_string(index=False) if patients else "No patients.")

def book_appointment():
    patients = load(PATIENTS)
    if not patients:
        print("Register a patient first.")
        return
    view_patients()
    pid = input("Patient ID: ").upper()
    if not any(p["id"] == pid for p in patients):
        print("Patient ID not found.")
        return
    doctor = input("Doctor name/specialization: ")
    date = input("Date (YYYY-MM-DD): ")
    records = load(APPOINTMENTS)
    aid = "A" + str(len(records) + 1).zfill(3)
    appt = Appointment(aid, pid, doctor, date)
    records.append({
        "appointment_id": appt.aid, "patient_id": appt.pid,
        "doctor": appt.doctor, "date": appt.date, "arrival": "",
        "start": "", "status": appt.status, "waiting": ""
    })
    save(APPOINTMENTS, records)
    print("Appointment booked. ID:", aid)

def view_appointments():
    records = load(APPOINTMENTS)
    print(pd.DataFrame(records).to_string(index=False) if records else "No appointments.")

def update_flow():
    records = load(APPOINTMENTS)
    aid = input("Appointment ID: ").upper()
    for a in records:
        if a["appointment_id"] == aid:
            print("1. Patient arrived\n2. Consultation started")
            choice = input("Choose: ")
            now = datetime.now().strftime("%H:%M")
            if choice == "1":
                a["arrival"], a["status"] = now, "Waiting"
                print("Arrival recorded.")
            elif choice == "2" and a["arrival"]:
                a["start"], a["status"] = now, "Completed"
                t1 = datetime.strptime(a["arrival"], "%H:%M")
                t2 = datetime.strptime(now, "%H:%M")
                a["waiting"] = int((t2-t1).total_seconds()/60) % 1440
                print("Waiting time:", a["waiting"], "minutes")
            else:
                print("Record arrival first.")
            save(APPOINTMENTS, records)
            return
    print("Appointment not found.")

def analytics():
    records = load(APPOINTMENTS)
    if not records:
        print("No data available.")
        return
    df = pd.DataFrame(records)
    print("Total appointments:", len(df))
    print("\nStatus summary:\n", df["status"].value_counts())
    waiting = pd.to_numeric(df["waiting"], errors="coerce").dropna()
    if not waiting.empty:
        print("Average waiting time:", round(waiting.mean(), 2), "minutes")
    print("\nAppointments by doctor:\n", df["doctor"].value_counts())

def main():
    while True:
        print("\n===== HOSPITAL APPOINTMENT SYSTEM =====")
        print("1.Register patient  2.View patients")
        print("3.Book appointment  4.View appointments")
        print("5.Update patient flow  6.Hospital analysis")
        print("0.Exit")
        choice = input("Enter choice: ")
        if choice == "1": register_patient()
        elif choice == "2": view_patients()
        elif choice == "3": book_appointment()
        elif choice == "4": view_appointments()
        elif choice == "5": update_flow()
        elif choice == "6": analytics()
        elif choice == "0":
            print("Thank you!")
            break
        else: print("Invalid choice.")

if __name__ == "__main__":
    main()
