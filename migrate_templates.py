import re
import os
import codecs

def process_file(src, dest, mode):
    with codecs.open(src, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Generic Replacements for Django
    
    if mode == 'register':
        # Find the form tag and add CSRF and method POST
        content = re.sub(
            r'<form[^>]*>', 
            r'<form method="POST" enctype="multipart/form-data">\n    {% csrf_token %}', 
            content, count=1
        )
        # Update input names to match Django form:
        # Full Name -> name
        content = re.sub(r'name="fullName"', 'name="name"', content)
        # Email Address -> email
        content = re.sub(r'name="emailAddress"', 'name="email"', content)
        # Phone Number -> phone
        content = re.sub(r'name="phoneNumber"', 'name="phone"', content)
        # Incident Title -> title
        content = re.sub(r'name="incidentTitle"', 'name="title"', content)
        # Incident Description -> description
        content = re.sub(r'name="incidentDescription"', 'name="description"', content)
        # Incident Location -> location
        content = re.sub(r'name="incidentLocation"', 'name="location"', content)
        # Evidence Files -> evidence
        content = re.sub(r'name="evidenceFiles"', 'name="evidence"', content)

        # Update URLs in navbar if they exist
        content = re.sub(r'href="#"', r'href="/"', content)
        
    elif mode == 'list':
        # Replace the hardcoded table body with a loop
        tbody_match = re.search(r'<tbody[^>]*>.*?</tbody\s*>', content, re.DOTALL)
        if tbody_match:
            tbody_content = tbody_match.group(0)
            
            # The structure of the row in the template needs to be extracted.
            # We'll just replace the entire tbody with a Django loop.
            
            django_tbody = """
            <tbody class="divide-y divide-outline-variant bg-surface-container-lowest">
                {% for complaint in complaints %}
                <tr class="hover:bg-surface-container-low transition-colors duration-150">
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="h-10 w-10 flex-shrink-0 rounded-full bg-primary-container flex items-center justify-center">
                                <span class="material-symbols-outlined text-on-primary-container">shield</span>
                            </div>
                            <div class="ml-4">
                                <div class="text-sm font-medium text-on-surface">{{ complaint.title }}</div>
                                <div class="text-sm text-on-surface-variant font-code-sm">ID: CYB-{{ complaint.id|stringformat:"04d" }}</div>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-on-surface">{{ complaint.name }}</div>
                        <div class="text-sm text-on-surface-variant">{{ complaint.location }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-on-surface">{{ complaint.created_at|date:"M d, Y" }}</div>
                        <div class="text-sm text-on-surface-variant">{{ complaint.created_at|time:"H:i" }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        {% if complaint.status == 'Pending' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-tertiary-fixed text-on-tertiary-fixed">
                                Pending
                            </span>
                        {% elif complaint.status == 'In Progress' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary-fixed text-on-secondary-fixed">
                                In Progress
                            </span>
                        {% elif complaint.status == 'Resolved' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Resolved
                            </span>
                        {% else %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-error-container text-on-error-container">
                                {{ complaint.status }}
                            </span>
                        {% endif %}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <a href="#" class="text-secondary hover:text-primary transition-colors flex items-center justify-end group">
                            Details
                            <span class="material-symbols-outlined ml-1 text-[18px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="5" class="px-6 py-8 text-center text-on-surface-variant">
                        No complaints found.
                    </td>
                </tr>
                {% endfor %}
            </tbody>
            """
            content = content.replace(tbody_content, django_tbody)
            
    elif mode == 'portal':
        # Same logic for portal, loop through complaints
        tbody_match = re.search(r'<tbody[^>]*>.*?</tbody\s*>', content, re.DOTALL)
        if tbody_match:
            tbody_content = tbody_match.group(0)
            
            django_tbody = """
            <tbody class="divide-y divide-outline-variant bg-surface-container-lowest">
                {% for complaint in complaints %}
                <tr class="hover:bg-surface-container-low transition-colors duration-150">
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-medium text-on-surface">CYB-{{ complaint.id|stringformat:"04d" }}</div>
                        <div class="text-xs text-on-surface-variant font-code-sm">{{ complaint.created_at|date:"Y-m-d H:i" }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <span class="material-symbols-outlined text-outline mr-2 text-[18px]">warning</span>
                            <span class="text-sm text-on-surface">{{ complaint.title }}</span>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-on-surface">{{ complaint.location }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        {% if complaint.status == 'Pending' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-tertiary-fixed text-on-tertiary-fixed">
                                Pending
                            </span>
                        {% elif complaint.status == 'In Progress' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary-fixed text-on-secondary-fixed">
                                In Progress
                            </span>
                        {% elif complaint.status == 'Resolved' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Resolved
                            </span>
                        {% else %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-error-container text-on-error-container">
                                {{ complaint.status }}
                            </span>
                        {% endif %}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-on-surface-variant">
                        {% if complaint.officer_assigned %}
                            {{ complaint.officer_assigned.name }}
                        {% else %}
                            Unassigned
                        {% endif %}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button class="text-secondary hover:bg-secondary-container hover:text-on-secondary-container px-3 py-1 rounded-md transition-colors mr-2">
                            Review
                        </button>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="6" class="px-6 py-8 text-center text-on-surface-variant">
                        No complaints found in the system.
                    </td>
                </tr>
                {% endfor %}
            </tbody>
            """
            content = content.replace(tbody_content, django_tbody)
            
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(content)

base_dir = 'c:/Users/ASUS/OneDrive/Desktop/CyberCrime/CyberCrime'

# 1. Register Complaint
src1 = f'{base_dir}/new_templates/official_complaint_registration/code.html'
dst1 = f'{base_dir}/complaint/templates/complaints/register_complaint.html'
process_file(src1, dst1, 'register')

# 2. Complaint List (Dashboard)
src2 = f'{base_dir}/new_templates/user_complaint_management_dashboard/code.html'
dst2 = f'{base_dir}/complaint/templates/complaints/complaint_list.html'
process_file(src2, dst2, 'list')

# 3. Sentinel Portal
src3 = f'{base_dir}/new_templates/sentinel_secure_official_portal/code.html'
dst3 = f'{base_dir}/complaint/templates/complaints/officer_dashboard.html'
process_file(src3, dst3, 'portal')

print("All templates processed and written successfully!")
