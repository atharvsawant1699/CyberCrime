from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from complaint.models import Officer, CaseType, CaseAssignmentHistory, Complaint
from complaint.context_processors import officer_status

class OfficerAccessTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create different test users
        self.anonymous_user = User.objects.create_user(username='anon', email='anon@example.com', password='password')
        self.normal_user = User.objects.create_user(username='normal', email='normal@example.com', password='password')
        self.staff_user = User.objects.create_user(username='staff', email='staff@example.com', password='password', is_staff=True)
        self.superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        
        # Create group
        self.officer_group, _ = Group.objects.get_or_create(name='Officers')
        self.group_user = User.objects.create_user(username='group_user', email='group_user@example.com', password='password')
        self.group_user.groups.add(self.officer_group)
        
        # Create registered officer email
        self.officer_email = 'registered@example.com'
        self.db_officer = Officer.objects.create(
            name="Officer John",
            badge_number="B12345",
            email=self.officer_email,
            phone="1234567890",
            department="Cyber Crime",
            Station_code="ST123"
        )
        self.registered_officer_user = User.objects.create_user(
            username='officer_john',
            email=self.officer_email,
            password='password'
        )

    def test_context_processor_anonymous(self):
        request = self.factory.get('/')
        request.user = self.anonymous_user
        # Simulate anonymous user (not authenticated yet)
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        context = officer_status(request)
        self.assertFalse(context['is_officer'])

    def test_context_processor_normal_user(self):
        request = self.factory.get('/')
        request.user = self.normal_user
        context = officer_status(request)
        self.assertFalse(context['is_officer'])

    def test_context_processor_staff_user(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        context = officer_status(request)
        self.assertTrue(context['is_officer'])

    def test_context_processor_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        context = officer_status(request)
        self.assertTrue(context['is_officer'])

    def test_context_processor_group_user(self):
        request = self.factory.get('/')
        request.user = self.group_user
        context = officer_status(request)
        self.assertTrue(context['is_officer'])

    def test_context_processor_registered_db_officer(self):
        request = self.factory.get('/')
        request.user = self.registered_officer_user
        context = officer_status(request)
        self.assertTrue(context['is_officer'])

    def test_officer_dashboard_redirect_anonymous(self):
        response = self.client.get(reverse('officer'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_officer_dashboard_access_denied_normal_user(self):
        self.client.login(username='normal', password='password')
        response = self.client.get(reverse('officer'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_officer_dashboard_access_allowed_staff(self):
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('officer'))
        self.assertEqual(response.status_code, 200)

    def test_officer_dashboard_access_allowed_registered_db_officer(self):
        self.client.login(username='officer_john', password='password')
        response = self.client.get(reverse('officer'))
        self.assertEqual(response.status_code, 200)


class CaseAllocationAndReassignmentTests(TestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        self.officer_user_1 = User.objects.create_user(username='officer1', email='officer1@example.com', password='password')
        self.officer_user_2 = User.objects.create_user(username='officer2', email='officer2@example.com', password='password')
        self.citizen_user = User.objects.create_user(username='citizen', email='citizen@example.com', password='password')

        # Create Officers
        self.officer_1 = Officer.objects.create(
            user=self.officer_user_1,
            officer_id="OFF-001",
            full_name="Officer Amit",
            department="Cyber Cell",
            rank="Inspector",
            specialization="Banking Fraud"
        )
        self.officer_2 = Officer.objects.create(
            user=self.officer_user_2,
            officer_id="OFF-002",
            full_name="Officer Rahul",
            department="Cyber Cell",
            rank="Sub-Inspector",
            specialization="Phishing"
        )

        # Create CaseTypes
        self.case_type_banking = CaseType.objects.create(
            name="Banking Fraud",
            description="Banking related online frauds",
            assigned_officer=self.officer_1,
            priority_level="High"
        )
        self.case_type_phishing = CaseType.objects.create(
            name="Phishing",
            description="Phishing links and sites",
            assigned_officer=self.officer_2,
            priority_level="Medium"
        )

    def test_automatic_case_allocation(self):
        # Submit a complaint under Banking Fraud
        complaint = Complaint.objects.create(
            user=self.citizen_user,
            case_type=self.case_type_banking,
            title="ATM Card Block Scam",
            description="Got call asking for OTP...",
            location="Mumbai"
        )
        # Verify auto-allocation took place
        self.assertEqual(complaint.assigned_officer, self.officer_1)
        self.assertEqual(complaint.status, "Assigned")
        self.assertEqual(complaint.priority, "High") # Inherited priority
        self.assertTrue(complaint.complaint_id.startswith("CYB"))

    def test_fallback_automatic_case_allocation(self):
        # Disable officer_2 (toggled unavailable)
        self.officer_2.availability_status = False
        self.officer_2.save()

        # Create officer_3 who has the same specialization and is available
        officer_user_3 = User.objects.create_user(username='officer3', email='officer3@example.com', password='password')
        officer_3 = Officer.objects.create(
            user=officer_user_3,
            officer_id="OFF-003",
            full_name="Officer Dinesh",
            department="Cyber Cell",
            rank="Inspector",
            specialization="Phishing"
        )

        # Submit a complaint under Phishing
        complaint = Complaint.objects.create(
            user=self.citizen_user,
            case_type=self.case_type_phishing,
            title="Suspicious Mail",
            description="Received phishing email",
            location="Delhi"
        )
        # Should fall back to Officer 3 because Officer 2 is unavailable
        self.assertEqual(complaint.assigned_officer, officer_3)

    def test_case_reassignment_history_log(self):
        # Submit complaint
        complaint = Complaint.objects.create(
            user=self.citizen_user,
            case_type=self.case_type_banking,
            title="ATM Card Block Scam",
            description="OTP fraud",
            location="Mumbai"
        )
        
        # Simulate reassign_case view post logic
        previous_officer = complaint.assigned_officer
        complaint.assigned_officer = self.officer_2
        complaint.status = "Assigned"
        complaint.save()

        # Log history
        CaseAssignmentHistory.objects.create(
            complaint=complaint,
            previous_officer=previous_officer,
            new_officer=self.officer_2,
            changed_by_admin=self.admin_user,
            reason="Workload Distribution"
        )

        # Verify history is saved
        histories = CaseAssignmentHistory.objects.filter(complaint=complaint)
        self.assertEqual(histories.count(), 1)
        history = histories.first()
        self.assertEqual(history.previous_officer, self.officer_1)
        self.assertEqual(history.new_officer, self.officer_2)
        self.assertEqual(history.changed_by_admin, self.admin_user)
        self.assertEqual(history.reason, "Workload Distribution")
