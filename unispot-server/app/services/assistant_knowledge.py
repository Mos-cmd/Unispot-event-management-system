"""Comprehensive static website knowledge base for the in-app assistant.

Covers every route, feature, workflow, role, and setting on UniSpot so the
assistant can answer questions about the whole site, not just bookings.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SitePage:
    path: str
    title: str
    description: str
    how_to: str
    keywords: tuple[str, ...] = ()
    roles: tuple[str, ...] = ("public",)
    requires_auth: bool = False


@dataclass(frozen=True)
class FaqEntry:
    question: str
    answer: str
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class RoleGuide:
    role: str
    description: str
    can_do: tuple[str, ...]
    dashboards: tuple[str, ...]
    keywords: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

PUBLIC_PAGES = (
    SitePage(
        path="/",
        title="Home",
        description=(
            "Public landing page introducing UniSpot. Shows featured events, "
            "venues, organizations, and services with links to sign up or log in."
        ),
        how_to="Open the site root. No login required.",
        keywords=("home", "landing", "front page", "welcome", "intro"),
    ),
    SitePage(
        path="/events",
        title="Events Directory",
        description=(
            "Browse public campus events. Each card shows organizer, venue, "
            "date/time, capacity, and registration status. Click a card for "
            "event details."
        ),
        how_to="Go to /events from the home page or navigation. No login required.",
        keywords=("events", "event directory", "browse events", "campus events"),
    ),
    SitePage(
        path="/events/:id",
        title="Event Detail",
        description=(
            "Full event page with date/time, venue, expected attendance, "
            "organizer, description, and registration button when open."
        ),
        how_to="Open /events/:id from the events directory or a shared link.",
        keywords=("event detail", "event page", "view event", "event information"),
    ),
    SitePage(
        path="/venues",
        title="Venues Directory",
        description=(
            "Browse campus venues with capacity, location, facilities, and "
            "availability. Each venue links to its detail page."
        ),
        how_to="Go to /venues from home or navigation. Filter by capacity or location.",
        keywords=("venues", "venue directory", "browse venues", "campus venues"),
    ),
    SitePage(
        path="/venues/:id",
        title="Venue Detail",
        description=(
            "Full venue page with capacity, location, facilities, photos, "
            "availability, and booking options for organizers."
        ),
        how_to="Open /venues/:id from the venues directory.",
        keywords=("venue detail", "venue page", "view venue"),
    ),
    SitePage(
        path="/organizations",
        title="Organizations",
        description=(
            "List of campus organizations. Organizers see memberships and can "
            "manage their organization's events and venues."
        ),
        how_to="Go to /organizations to browse or view memberships.",
        keywords=("organizations", "clubs", "groups", "membership"),
    ),
)

# ---------------------------------------------------------------------------
# Auth pages
# ---------------------------------------------------------------------------

AUTH_PAGES = (
    SitePage(
        path="/login",
        title="Login",
        description="Sign in with email and password.",
        how_to="Go to /login and enter your credentials.",
        keywords=("login", "sign in", "log in", "credentials"),
    ),
    SitePage(
        path="/signup",
        title="Sign Up",
        description=(
            "Public account creation. New accounts are created as active "
            "students. Organizer access requires an active organizer membership."
        ),
        how_to="Go to /signup and complete the registration form.",
        keywords=("signup", "sign up", "register", "create account"),
    ),
    SitePage(
        path="/forgot-password",
        title="Forgot Password",
        description="Request a password reset link sent to your email.",
        how_to="Go to /forgot-password and enter your email address.",
        keywords=("forgot password", "reset password", "password reset"),
    ),
    SitePage(
        path="/reset-password",
        title="Reset Password",
        description="Set a new password using a valid reset token from email.",
        how_to="Open the reset link from your email and set a new password.",
        keywords=("reset password", "new password", "reset link"),
    ),
    SitePage(
        path="/verify-email",
        title="Verify Email",
        description="Verify your email address using a verification token.",
        how_to="Open the verification link from your email.",
        keywords=("verify email", "email verification", "confirm email"),
    ),
    SitePage(
        path="/access-denied",
        title="Access Denied",
        description="Shown when you try to reach a page your role cannot access.",
        how_to="You land here automatically if you lack the required role.",
        keywords=("access denied", "forbidden", "unauthorized"),
    ),
    SitePage(
        path="/notifications",
        title="My Notifications",
        description=(
            "View in-app notifications: booking updates, event changes, service "
            "request status changes, certificate issuances."
        ),
        how_to="Go to /notifications while signed in.",
        requires_auth=True,
        keywords=("notifications", "my notifications", "alerts"),
    ),
    SitePage(
        path="/notifications/:id/read",
        title="Mark Notification Read",
        description="Mark a specific notification as read.",
        how_to="Open /notifications/:id/read from your notifications list.",
        requires_auth=True,
        keywords=("mark read", "notification read", "dismiss"),
    ),
)

# ---------------------------------------------------------------------------
# Student pages
# ---------------------------------------------------------------------------

STUDENT_PAGES = (
    SitePage(
        path="/student/dashboard",
        title="Student Dashboard",
        description=(
            "Student home showing upcoming events, registrations, and quick "
            "links to browse events and venues."
        ),
        how_to="Sign in as a student and go to /student/dashboard.",
        roles=("student",),
        requires_auth=True,
        keywords=("student dashboard", "student home", "my events", "my registrations"),
    ),
    SitePage(
        path="/my-waitlists",
        title="My Waitlists",
        description="View event waitlists you've joined and your position.",
        how_to="Go to /my-waitlists while signed in.",
        requires_auth=True,
        keywords=("my waitlists", "waitlist", "waiting list"),
    ),
    SitePage(
        path="/services/event-registration",
        title="Event Registration",
        description="Register for events and manage your event registrations.",
        how_to="Go to /services/event-registration to sign up for events.",
        roles=("student", "organizer", "venue_admin", "system_admin"),
        requires_auth=True,
        keywords=("event registration", "register for event", "sign up for event"),
    ),
)

# ---------------------------------------------------------------------------
# Organizer pages
# ---------------------------------------------------------------------------

ORGANIZER_PAGES = (
    SitePage(
        path="/organizer/dashboard",
        title="Organizer Dashboard",
        description=(
            "Organizer home. Manage events, venue bookings, service requests, "
            "and event-day attendance/check-in. Create new events with optional "
            "venue reservation."
        ),
        how_to="Sign in as an organizer with an active membership, then /organizer/dashboard.",
        roles=("organizer", "venue_admin"),
        requires_auth=True,
        keywords=("organizer dashboard", "organizer home", "manage events"),
    ),
    SitePage(
        path="/booking/new",
        title="New Booking",
        description=(
            "Create a venue booking for an event. Select venue, organization, "
            "event name, expected attendance, date, start time, and end time."
        ),
        how_to="Go to /booking/new while signed in as an organizer.",
        roles=("organizer", "venue_admin"),
        requires_auth=True,
        keywords=("new booking", "create booking", "book venue", "booking/new"),
    ),
    SitePage(
        path="/services",
        title="Services Directory",
        description=(
            "Browse campus services (catering, AV, security, cleaning, etc.). "
            "Organizers can request a service and track quote/fulfillment."
        ),
        how_to="Go to /services while signed in as an organizer.",
        roles=("organizer", "venue_admin"),
        requires_auth=True,
        keywords=("services", "service directory", "catering", "AV", "security"),
    ),
    SitePage(
        path="/services/:serviceId",
        title="Service Detail & Request",
        description=(
            "Service page showing what the provider offers and a request form "
            "for organizers."
        ),
        how_to="Open /services/:serviceId from the services directory.",
        roles=("organizer", "venue_admin"),
        requires_auth=True,
        keywords=("service detail", "request service", "service request"),
    ),
    SitePage(
        path="/services/analytics",
        title="Service Analytics",
        description="View service usage analytics and provider performance metrics.",
        how_to="Go to /services/analytics from the services section.",
        roles=("organizer", "venue_admin", "service_provider", "system_admin"),
        requires_auth=True,
        keywords=("service analytics", "service metrics", "provider performance"),
    ),
    SitePage(
        path="/services/certificates",
        title="Digital Certificates",
        description="Issue and verify digital certificates for event participation or service completion.",
        how_to="Go to /services/certificates to issue or verify a certificate.",
        roles=("organizer", "venue_admin", "student", "service_provider", "system_admin"),
        requires_auth=True,
        keywords=("certificates", "digital certificate", "issue certificate", "verify certificate"),
    ),
    SitePage(
        path="/services/equipment",
        title="Equipment Reservations",
        description="Reserve equipment (projectors, microphones, tables, chairs) for events.",
        how_to="Go to /services/equipment to browse and reserve equipment.",
        roles=("organizer", "venue_admin"),
        requires_auth=True,
        keywords=("equipment", "reserve equipment", "projector", "microphone", "tables", "chairs"),
    ),
    SitePage(
        path="/services/qr-attendance",
        title="QR Attendance",
        description="Check in attendees using QR codes for event-day attendance management.",
        how_to="Go to /services/qr-attendance to scan or generate QR codes for check-in.",
        roles=("organizer", "venue_admin", "system_admin"),
        requires_auth=True,
        keywords=("QR attendance", "check in", "attendance", "QR code", "event-day"),
    ),
    SitePage(
        path="/services/waitlists",
        title="Waitlists & Recurring",
        description="Manage event waitlists and recurring event schedules.",
        how_to="Go to /services/waitlists to view waitlists or set up recurring events.",
        roles=("organizer", "venue_admin", "system_admin"),
        requires_auth=True,
        keywords=("waitlist", "recurring event", "event schedule", "waiting list"),
    ),
    SitePage(
        path="/services/directory",
        title="Service Provider Directory",
        description="Browse approved service providers and their offerings.",
        how_to="Go to /services/directory to browse providers.",
        roles=("organizer", "venue_admin"),
        requires_auth=True,
        keywords=("service provider directory", "browse providers", "provider directory"),
    ),
)

# ---------------------------------------------------------------------------
# Provider pages
# ---------------------------------------------------------------------------

PROVIDER_PAGES = (
    SitePage(
        path="/provider/dashboard",
        title="Provider Dashboard",
        description=(
            "Service provider home. View assigned service requests, update "
            "their status, and submit quotes for fulfillment."
        ),
        how_to="Sign in as an approved service provider, then /provider/dashboard.",
        roles=("service_provider",),
        requires_auth=True,
        keywords=("provider dashboard", "service provider", "assigned requests", "submit quote"),
    ),
    SitePage(
        path="/provider/requests",
        title="Provider Requests",
        description="View service requests assigned to you as a provider.",
        how_to="Go to /provider/requests while signed in as a service provider.",
        roles=("service_provider",),
        requires_auth=True,
        keywords=("provider requests", "assigned requests", "service requests"),
    ),
)

# ---------------------------------------------------------------------------
# Admin pages
# ---------------------------------------------------------------------------

ADMIN_SECTIONS = (
    SitePage(
        path="/admin",
        title="Admin Dashboard",
        description="System administration overview with quick access to all sections.",
        how_to="Sign in as a system admin, then /admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin", "admin dashboard", "system administration"),
    ),
    SitePage(
        path="/admin/events",
        title="Admin Events",
        description="Manage all campus events: create, edit, cancel, view registrations.",
        how_to="Go to /admin/events as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin events", "manage events", "all events"),
    ),
    SitePage(
        path="/admin/bookings",
        title="Admin Bookings",
        description="Manage all venue bookings: view, cancel, release slots, audit.",
        how_to="Go to /admin/bookings as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin bookings", "manage bookings", "all bookings"),
    ),
    SitePage(
        path="/admin/audit",
        title="Admin Audit Log",
        description="View system audit events: who did what and when.",
        how_to="Go to /admin/audit as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin audit", "audit log", "audit events"),
    ),
    SitePage(
        path="/admin/allocations",
        title="Admin Allocations",
        description="Manage resource allocations across events and venues.",
        how_to="Go to /admin/allocations as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin allocations", "resource allocations", "allocation management"),
    ),
    SitePage(
        path="/admin/registrations",
        title="Admin Registrations",
        description="View and manage all event registrations across the platform.",
        how_to="Go to /admin/registrations as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin registrations", "manage registrations", "all registrations"),
    ),
    SitePage(
        path="/admin/equipment",
        title="Admin Equipment",
        description="Manage equipment inventory and reservations.",
        how_to="Go to /admin/equipment as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin equipment", "equipment inventory", "equipment management"),
    ),
    SitePage(
        path="/admin/waitlists",
        title="Admin Waitlists & Recurring",
        description="Manage event waitlists and recurring event schedules.",
        how_to="Go to /admin/waitlists as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin waitlists", "recurring events", "waitlist management"),
    ),
    SitePage(
        path="/admin/policies",
        title="Admin Policies",
        description="Create and manage booking and platform policy rules.",
        how_to="Go to /admin/policies as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin policies", "policy rules", "booking policy"),
    ),
    SitePage(
        path="/admin/maintenance",
        title="Admin Maintenance",
        description="Record and track venue/maintenance windows and impacts.",
        how_to="Go to /admin/maintenance as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin maintenance", "maintenance records", "maintenance windows"),
    ),
    SitePage(
        path="/admin/certificates",
        title="Admin Certificates",
        description="Manage issued digital certificates and revocations.",
        how_to="Go to /admin/certificates as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin certificates", "certificate management", "revoke certificate"),
    ),
    SitePage(
        path="/admin/providers",
        title="Admin Service Providers",
        description="Create, approve, suspend, and manage service providers.",
        how_to="Go to /admin/providers as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin providers", "service providers", "provider management"),
    ),
    SitePage(
        path="/admin/service-requests",
        title="Admin Service Requests",
        description="View and manage all service requests across the platform.",
        how_to="Go to /admin/service-requests as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin service requests", "manage service requests", "request management"),
    ),
    SitePage(
        path="/admin/settings",
        title="Admin System Settings",
        description="Configure platform-wide settings and configuration.",
        how_to="Go to /admin/settings as a system admin.",
        roles=("system_admin",),
        requires_auth=True,
        keywords=("admin settings", "system settings", "platform configuration"),
    ),
)

ALL_ADMIN = (*ADMIN_SECTIONS,)

# ---------------------------------------------------------------------------
# FAQs
# ---------------------------------------------------------------------------

FAQS = (
    FaqEntry(
        question="What is UniSpot?",
        answer=(
            "UniSpot is a campus event-management platform. Public visitors can "
            "browse events, venues, organizations, and services without logging "
            "in. Signed-in users get role-based dashboards: students register "
            "for events; organizers create events, book venues, and request "
            "services; service providers fulfill requests; system admins "
            "administer the platform from /admin."
        ),
        keywords=("what is", "unispot", "platform", "overview", "what does it do"),
    ),
    FaqEntry(
        question="How do I create an account?",
        answer=(
            "Go to /signup and complete the registration form. New accounts are "
            "created as active students. Organizer access requires an active "
            "organizer membership in an organization."
        ),
        keywords=("create account", "signup", "sign up", "register", "new account", "join"),
    ),
    FaqEntry(
        question="How do I log in?",
        answer=(
            "Go to /login and enter your email and password. If you forgot your "
            "password, use /forgot-password to receive a reset link by email."
        ),
        keywords=("log in", "login", "sign in", "credentials", "password"),
    ),
    FaqEntry(
        question="How do I book a venue?",
        answer=(
            "1. Go to /venues and find a venue.\n"
            "2. Open the venue detail page (/venues/:id).\n"
            "3. Click Book to open /booking/new.\n"
            "4. Select your organization, enter event name, expected "
            "attendance, date, start time, and end time.\n"
            "5. Submit the booking.\n\nYou must be signed in as an organizer "
            "with an active membership in an organization."
        ),
        keywords=("book venue", "reserve venue", "venue booking", "how to book", "booking"),
    ),
    FaqEntry(
        question="How do I register for an event?",
        answer=(
            "Go to /events, open an event detail page, and click the "
            "registration button if registration is open. You can also manage "
            "registrations at /services/event-registration."
        ),
        keywords=("register for event", "event registration", "sign up for event", "attend event"),
    ),
    FaqEntry(
        question="How do I request a service?",
        answer=(
            "1. Go to /services and browse available services.\n"
            "2. Open a service detail page (/services/:serviceId).\n"
            "3. Fill out the request form with your event details.\n"
            "4. Submit the request. A provider will review it and may send a "
            "quote.\n\nYou must be signed in as an organizer with an active "
            "membership."
        ),
        keywords=("request service", "service request", "how to request", "catering", "AV", "security"),
    ),
    FaqEntry(
        question="What can a student do?",
        answer=(
            "Students can browse public events and venues, register for events, "
            "view their registrations, join waitlists, and access digital "
            "certificates from /student/dashboard."
        ),
        keywords=("student", "what can a student do", "student role", "student capabilities"),
    ),
    FaqEntry(
        question="What can an organizer do?",
        answer=(
            "Organizers (with an active membership in an organization) can "
            "create events, book venues, request services, manage event-day "
            "attendance and check-in, and view service requests from "
            "/organizer/dashboard."
        ),
        keywords=("organizer", "what can an organizer do", "organizer role", "organizer capabilities"),
    ),
    FaqEntry(
        question="What can a service provider do?",
        answer=(
            "Service providers receive assigned service requests, update their "
            "status, and submit quotes for fulfillment from /provider/dashboard."
        ),
        keywords=("service provider", "provider", "what can a provider do", "provider role"),
    ),
    FaqEntry(
        question="What can a system admin do?",
        answer=(
            "System admins manage the whole platform from /admin: events, "
            "bookings, audit, allocations, registrations, equipment, waitlists, "
            "policies, maintenance, certificates, providers, service requests, "
            "and system settings."
        ),
        keywords=("admin", "system admin", "what can an admin do", "admin role", "administrator"),
    ),
    FaqEntry(
        question="How do I reset my password?",
        answer=(
            "Go to /forgot-password and enter your email. You'll receive a reset "
            "link. Open the link and go to /reset-password to set a new password."
        ),
        keywords=("reset password", "forgot password", "new password", "lost password"),
    ),
    FaqEntry(
        question="How do I verify my email?",
        answer=(
            "Open the verification link sent to your email after signup. This "
            "takes you to /verify-email to confirm your address."
        ),
        keywords=("verify email", "email verification", "confirm email", "verification link"),
    ),
    FaqEntry(
        question="Who can access /admin?",
        answer=(
            "Only users with the system_admin role can access /admin. If you "
            "try without that role, you'll be redirected to /access-denied."
        ),
        keywords=("admin access", "who can access admin", "system admin", "access-denied"),
    ),
    FaqEntry(
        question="Where are my notifications?",
        answer=(
            "Go to /notifications to view your in-app notifications, including "
            "booking updates, event changes, service request status changes, and "
            "certificate issuances."
        ),
        keywords=("notifications", "my notifications", "alerts", "where are notifications"),
    ),
    FaqEntry(
        question="How do I check in attendees at an event?",
        answer=(
            "Go to /services/qr-attendance to scan QR codes or generate check-in "
            "codes for event-day attendance management. You must be an organizer "
            "or system admin."
        ),
        keywords=("check in", "attendance", "QR attendance", "event-day", "check-in"),
    ),
    FaqEntry(
        question="How do I issue a digital certificate?",
        answer=(
            "Go to /services/certificates. Certificates can be issued for "
            "confirmed event registrations or service completions. Use the "
            "verify tab to check a certificate code publicly."
        ),
        keywords=("issue certificate", "digital certificate", "certificate", "verify certificate"),
    ),
    FaqEntry(
        question="How do I reserve equipment?",
        answer=(
            "Go to /services/equipment to browse available equipment (projectors, "
            "microphones, tables, chairs, etc.) and reserve items for your event."
        ),
        keywords=("reserve equipment", "equipment", "projector", "microphone", "tables", "chairs"),
    ),
    FaqEntry(
        question="How do I manage waitlists or recurring events?",
        answer=(
            "Go to /services/waitlists to view event waitlists and set up "
            "recurring event schedules."
        ),
        keywords=("waitlist", "recurring event", "waiting list", "event schedule"),
    ),
    FaqEntry(
        question="How do I check venue availability?",
        answer=(
            "Go to /venues and use filters to see availability, or ask me to "
            "check availability with a date, start time, and end time."
        ),
        keywords=("check availability", "availability", "available venue", "free venue"),
    ),
    FaqEntry(
        question="How do I view my bookings?",
        answer=(
            "Ask me 'my bookings' and I'll list your bookings, or go to the "
            "organizer dashboard at /organizer/dashboard to manage your venue "
            "bookings and service requests."
        ),
        keywords=("my bookings", "view bookings", "my reservations", "booking list"),
    ),
    FaqEntry(
        question="How do I cancel a booking?",
        answer=(
            "Provide the booking ID or confirmation reference and I'll help you "
            "cancel it. You must be the booking requester or a system admin."
        ),
        keywords=("cancel booking", "cancel reservation", "how to cancel"),
    ),
    FaqEntry(
        question="What is in the admin section?",
        answer=(
            "The admin section at /admin is for system admins only. It includes "
            "sections for events, bookings, audit log, allocations, registrations, "
            "equipment, waitlists and recurring schedules, policies, maintenance, "
            "certificates, service providers, service requests, and system "
            "settings."
        ),
        keywords=("admin section", "admin panel", "what is in admin", "admin areas"),
    ),
    FaqEntry(
        question="How do I manage policies?",
        answer=(
            "Go to /admin/policies as a system admin to create and manage booking "
            "and platform policy rules."
        ),
        keywords=("manage policies", "policy rules", "booking policy", "admin policies"),
    ),
    FaqEntry(
        question="How do I view the audit log?",
        answer=(
            "Go to /admin/audit as a system admin to view system audit events "
            "showing who did what and when."
        ),
        keywords=("view audit log", "audit log", "audit events", "admin audit"),
    ),
)

# ---------------------------------------------------------------------------
# Role guides
# ---------------------------------------------------------------------------

ROLE_GUIDES = (
    RoleGuide(
        role="student",
        description="Students can browse public events and venues, register for events, view registrations, join waitlists, and access digital certificates.",
        can_do=(
            "Browse events and venues without logging in",
            "Register for events",
            "View your registrations",
            "Join event waitlists",
            "Access digital certificates",
        ),
        dashboards=("/student/dashboard",),
        keywords=("student", "what can a student do", "student role", "student capabilities"),
    ),
    RoleGuide(
        role="organizer",
        description="Organizers (with an active membership in an organization) can create events, book venues, request services, and manage event-day attendance.",
        can_do=(
            "Create events with optional venue reservation",
            "Book venues for events",
            "Request services from the services directory",
            "Manage event-day attendance and QR check-in",
            "View and manage service requests",
        ),
        dashboards=("/organizer/dashboard",),
        keywords=("organizer", "what can an organizer do", "organizer role", "organizer capabilities"),
    ),
    RoleGuide(
        role="service_provider",
        description="Service providers receive assigned service requests, update their status, and submit quotes for fulfillment.",
        can_do=(
            "View assigned service requests",
            "Update request status",
            "Submit quotes for fulfillment",
        ),
        dashboards=("/provider/dashboard", "/provider/requests"),
        keywords=("service provider", "provider", "what can a provider do", "provider role"),
    ),
    RoleGuide(
        role="system_admin",
        description="System admins manage the whole platform from /admin.",
        can_do=(
            "Manage all events, bookings, and registrations",
            "View audit log and manage allocations",
            "Manage equipment, waitlists, and recurring schedules",
            "Create and manage policies and maintenance records",
            "Manage certificates, service providers, and service requests",
            "Configure system settings",
        ),
        dashboards=("/admin",),
        keywords=("admin", "system admin", "what can an admin do", "admin role", "administrator"),
    ),
)

# ---------------------------------------------------------------------------
# All pages index
# ---------------------------------------------------------------------------

ALL_PAGES = (
    *PUBLIC_PAGES,
    *AUTH_PAGES,
    *STUDENT_PAGES,
    *ORGANIZER_PAGES,
    *PROVIDER_PAGES,
    *ALL_ADMIN,
)

PAGES_BY_PATH = {page.path: page for page in ALL_PAGES}


def describe_page(page: SitePage) -> str:
    """Build a natural-language description of a page."""
    access = []
    if page.requires_auth:
        access.append("requires sign-in")
    if page.roles and page.roles != ("public",):
        access.append("for " + ", ".join(page.roles))
    access_text = " (" + "; ".join(access) + ")" if access else ""
    return (
        f"{page.title} ({page.path}){access_text}: {page.description} "
        f"How to reach it: {page.how_to}"
    )


SITE_OVERVIEW = (
    "UniSpot is a campus event-management platform. Public visitors can browse "
    "events, venues, organizations, and services without logging in. Signed-in "
    "users get role-based dashboards: students register for events; organizers "
    "create events, book venues, and request services; service providers "
    "fulfill requests; system admins administer the platform from /admin."
)


__all__ = [
    "SitePage",
    "FaqEntry",
    "RoleGuide",
    "ALL_PAGES",
    "PAGES_BY_PATH",
    "FAQS",
    "ROLE_GUIDES",
    "SITE_OVERVIEW",
    "describe_page",
]
