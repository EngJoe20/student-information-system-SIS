"""
Report generation utilities for PDF, CSV, and JSON formats.
"""
from io import BytesIO
import csv
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class TranscriptGenerator:
    """Generate student transcripts."""
    
    @staticmethod
    def generate_pdf(student):
        """Generate PDF transcript."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph("OFFICIAL TRANSCRIPT", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Student Information
        student_info = [
            ['Student Information', ''],
            ['Student ID:', student.student_id],
            ['Name:', student.user.full_name],
            ['Date of Birth:', student.date_of_birth.strftime('%m/%d/%Y')],
            ['Enrollment Date:', student.enrollment_date.strftime('%m/%d/%Y')],
            ['Academic Status:', student.get_academic_status_display()],
            ['Cumulative GPA:', f"{student.gpa:.2f}"],
        ]
        
        info_table = Table(student_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Academic Records
        enrollments = student.enrollments.filter(
            status__in=['COMPLETED', 'ENROLLED']
        ).order_by('class__academic_year', 'class__semester')
        
        # Group by semester
        semesters = {}
        for enrollment in enrollments:
            key = (enrollment.class_obj.academic_year, enrollment.class_obj.semester)
            if key not in semesters:
                semesters[key] = []
            semesters[key].append(enrollment)
        
        for (year, semester), semester_enrollments in sorted(semesters.items()):
            # Semester Header
            semester_header = Paragraph(
                f"<b>{semester} {year}</b>",
                styles['Heading2']
            )
            elements.append(semester_header)
            elements.append(Spacer(1, 0.2*inch))
            
            # Course Table
            course_data = [['Course Code', 'Course Name', 'Credits', 'Grade', 'Points']]
            semester_credits = 0
            semester_points = 0
            
            for enrollment in semester_enrollments:
                course = enrollment.class_obj.course
                course_data.append([
                    course.course_code,
                    course.course_name,
                    str(course.credits),
                    enrollment.grade or 'IP',
                    f"{enrollment.grade_points:.2f}" if enrollment.grade_points else '-'
                ])
                semester_credits += course.credits
                if enrollment.grade_points:
                    semester_points += enrollment.grade_points * course.credits
            
            semester_gpa = semester_points / semester_credits if semester_credits > 0 else 0
            
            course_data.append(['', 'Semester Totals:', str(semester_credits), '', f"{semester_gpa:.2f}"])
            
            course_table = Table(course_data, colWidths=[1.2*inch, 3*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            course_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(course_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}"
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_json(student):
        """Generate JSON transcript."""
        from students.serializers import StudentSerializer
        from students.models import Enrollment
        
        enrollments = Enrollment.objects.filter(
            student=student,
            status__in=['COMPLETED', 'ENROLLED']
        ).order_by('class__academic_year', 'class__semester')
        
        courses = []
        for enrollment in enrollments:
            courses.append({
                'semester': enrollment.class_obj.semester,
                'academic_year': enrollment.class_obj.academic_year,
                'course_code': enrollment.class_obj.course.course_code,
                'course_name': enrollment.class_obj.course.course_name,
                'credits': enrollment.class_obj.course.credits,
                'grade': enrollment.grade,
                'grade_points': float(enrollment.grade_points) if enrollment.grade_points else None
            })
        
        return {
            'student': StudentSerializer(student).data,
            'academic_summary': {
                'cumulative_gpa': float(student.gpa),
                'academic_status': student.academic_status
            },
            'courses': courses,
            'generated_at': datetime.now().isoformat()
        }


class AttendanceReportGenerator:
    """Generate attendance reports."""
    
    @staticmethod
    def generate_pdf(data):
        """Generate PDF attendance report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph("ATTENDANCE REPORT", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_data = [
            ['Period:', f"{data['period']['start_date']} to {data['period']['end_date']}"],
            ['Total Days:', str(data['summary']['total_days'])],
            ['Present:', str(data['summary']['present'])],
            ['Absent:', str(data['summary']['absent'])],
            ['Late:', str(data['summary']['late'])],
            ['Excused:', str(data['summary']['excused'])],
            ['Attendance Rate:', f"{data['summary']['attendance_percentage']:.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Details
        if data.get('details'):
            detail_data = [['Date', 'Course', 'Status']]
            for record in data['details']:
                detail_data.append([
                    record['date'],
                    record['course_name'],
                    record['status']
                ])
            
            detail_table = Table(detail_data, colWidths=[1.5*inch, 3.5*inch, 1.5*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(detail_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_csv(data):
        """Generate CSV attendance report."""
        output = BytesIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['Attendance Report'])
        writer.writerow(['Period', f"{data['period']['start_date']} to {data['period']['end_date']}"])
        writer.writerow([])
        
        # Summary
        writer.writerow(['Summary'])
        writer.writerow(['Total Days', data['summary']['total_days']])
        writer.writerow(['Present', data['summary']['present']])
        writer.writerow(['Absent', data['summary']['absent']])
        writer.writerow(['Late', data['summary']['late']])
        writer.writerow(['Excused', data['summary']['excused']])
        writer.writerow(['Attendance Rate', f"{data['summary']['attendance_percentage']:.1f}%"])
        writer.writerow([])
        
        # Details
        if data.get('details'):
            writer.writerow(['Date', 'Course', 'Status'])
            for record in data['details']:
                writer.writerow([
                    record['date'],
                    record['course_name'],
                    record['status']
                ])
        
        output.seek(0)
        return output


class GradeReportGenerator:
    """Generate grade reports."""
    
    @staticmethod
    def generate_pdf(data):
        """Generate PDF grade report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph("GRADE REPORT", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Class Information
        class_info = data['class']
        info_data = [
            ['Class Information', ''],
            ['Course:', f"{class_info['course_name']} ({class_info['class_code']})"],
            ['Section:', class_info['section']],
            ['Instructor:', class_info['instructor_name']],
            ['Semester:', f"{class_info['semester']} {class_info['academic_year']}"],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Statistics
        stats = data['statistics']
        stats_data = [
            ['Statistics', ''],
            ['Total Students:', str(stats['total_students'])],
            ['Average Grade:', f"{stats['average_grade']:.2f}%"],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 4*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Student Grades
        grade_data = [['Student ID', 'Student Name', 'Final Grade', 'Grade Points']]
        for student in data['student_grades']:
            grade_data.append([
                student['student_id'],
                student['student_name'],
                student['final_grade'] or 'N/A',
                f"{student['grade_points']:.2f}" if student['grade_points'] else 'N/A'
            ])
        
        grade_table = Table(grade_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
        grade_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(grade_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_csv(data):
        """Generate CSV grade report."""
        output = BytesIO()
        writer = csv.writer(output)
        
        # Class Information
        class_info = data['class']
        writer.writerow(['Grade Report'])
        writer.writerow(['Course', f"{class_info['course_name']} ({class_info['class_code']})"])
        writer.writerow(['Section', class_info['section']])
        writer.writerow(['Instructor', class_info['instructor_name']])
        writer.writerow([])
        
        # Statistics
        stats = data['statistics']
        writer.writerow(['Total Students', stats['total_students']])
        writer.writerow(['Average Grade', f"{stats['average_grade']:.2f}%"])
        writer.writerow([])
        
        # Student Grades
        writer.writerow(['Student ID', 'Student Name', 'Final Grade', 'Grade Points'])
        for student in data['student_grades']:
            writer.writerow([
                student['student_id'],
                student['student_name'],
                student['final_grade'] or 'N/A',
                f"{student['grade_points']:.2f}" if student['grade_points'] else 'N/A'
            ])
        
        output.seek(0)
        return output