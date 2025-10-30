from django.shortcuts import render, redirect
from django.utils import timezone
from .models import School, Events, Student, EventParticipants
from datetime import datetime
from django.db.models import Sum, Count
from django.contrib import messages


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    total_schools = School.objects.count()
    school = Student.objects.filter(student=request.user).first().school
    events = EventParticipants.objects.filter(student=request.user)
    waste = events.aggregate(total=Sum("event__waste_collected"))["total"] or 0
    student_ids = (
        EventParticipants.objects.filter(event__in=events.values("event"))
        .values_list("student", flat=True)
        .distinct()
    )
    latest_participated_events = []
    if len(events) >= 3:
        latest_participated_events.append(list(events)[len(list(events)) - 1].event)
        latest_participated_events.append(list(events)[len(list(events)) - 2].event)
        latest_participated_events.append(list(events)[len(list(events)) - 3].event)
    else:
        for event in events:
            latest_participated_events.append(event.event)
    schools_with_waste = School.objects.annotate(
        total_waste=Sum("events__waste_collected")
    ).order_by("-total_waste")
    print(schools_with_waste)
    rank = 1

    for current_school in schools_with_waste:
        if current_school.id == school.id:
            break
        else:
            rank = rank + 1

    event_notifications_getter = Events.objects.filter(date__gt = timezone.now().date())
    event_notifications = []
    for event in event_notifications_getter:
        participating = False
        for participant in EventParticipants.objects.filter(event=event):
            if participant.student == request.user:
                participating = True
                break
            else:
                continue
        if not participating:
            event_notifications.append(event)
    unregistered_events_count = len(event_notifications)
 
    return render(
        request,
        "dashboard.html",
        {
            "events_count": len(events),
            "waste": waste,
            "students_involved": len(student_ids),
            "latest_participated_events": latest_participated_events,
            "school": school,
            "school_rank": rank,
            "unregistered_events" : event_notifications,
            "unregistered_events_count" : unregistered_events_count, 
            "total_no_of_schools" : total_schools
        },
    )


def full_map(request):
    if not request.user.is_authenticated:
        return redirect("login")
    my_school = Student.objects.filter(student=request.user).first().school
    schools = School.objects.all()

    event_notifications_getter = Events.objects.filter(date__gt = timezone.now().date())
    events = []
    for event in event_notifications_getter:
        participating = False
        for participant in EventParticipants.objects.filter(event=event):
            if participant.student == request.user:
                participating = True
                break
            else:
                continue
        if not participating:
            events.append(event)
    unregistered_events_count = len(events)
    return render(
        request, "full-map.html", {"schools": schools, "my_school": my_school, "unregistered_events" : events,
            "unregistered_events_count" : unregistered_events_count}
    )


def events(request):
    if not request.user.is_authenticated:
        return redirect("login")
    school = Student.objects.get(student=request.user).school
    my_events = Events.objects.filter(organised_by=school).order_by('-created_at')
    all_events = Events.objects.exclude(organised_by=school).order_by('-created_at')

    for event in all_events:
        no_of_participants = EventParticipants.objects.filter(event=event).count()
        expected_participants = event.expected_participants
        if no_of_participants >= expected_participants:
            status = "Housefull"
        else:
            status = f"available - {expected_participants - no_of_participants}"
        event.status = status

    for event in my_events:
        no_of_participants = EventParticipants.objects.filter(event=event).count()
        expected_participants = event.expected_participants
        if no_of_participants >= expected_participants:
            status = "Housefull"
        else:
            status = f"available - {expected_participants - no_of_participants}"
        event.status = status
    event_notifications_getter = Events.objects.filter(date__gt = timezone.now().date())
    events = []
    for event in event_notifications_getter:
        participating = False
        for participant in EventParticipants.objects.filter(event=event):
            if participant.student == request.user:
                participating = True
                break
            else:
                continue
        if not participating:
            events.append(event)
    unregistered_events_count = len(events)

    return render(
        request,
        "events.html",
        {"global_events": all_events, "school_events": my_events, "unregistered_events" : events,
            "unregistered_events_count" : unregistered_events_count},
    )


def cleanup_by_school(request):
    if not request.user.is_authenticated:
        return redirect("login")
    school = Student.objects.filter(student=request.user).first().school
    events = (
        Events.objects.filter(organised_by=school)
        .order_by("-created_at")[:5]
        .annotate(participants=Count("eventparticipants"))
    )
    waste = {"total": 0, "plastic": 0, "paper": 0, "glass": 0, "miscellaneous": 0}
    for event in events:
        waste["total"] = waste["total"] + event.waste_collected
        waste["plastic"] = waste["plastic"] + event.plastic_collected
        waste["paper"] = waste["paper"] + event.paper_collected
        waste["glass"] = waste["glass"] + event.glass_collected
        waste["miscellaneous"] = waste["miscellaneous"] + event.miscellaneous_collected
    event_participants = EventParticipants.objects.none()
    for event in Events.objects.filter(organised_by=school):
        event_participants = event_participants | EventParticipants.objects.filter(
            event=event
        )
    event_participants = len(event_participants.values("student").distinct())

    schools_with_waste = School.objects.annotate(
        total_waste=Sum("events__waste_collected")
    ).order_by("-total_waste")
    print(schools_with_waste)
    rank = 1

    for current_school in schools_with_waste:
        if current_school.id == school.id:
            break
        else:
            rank = rank + 1
    
    event_notifications_getter = Events.objects.filter(date__gt = timezone.now().date())
    event_notifications = []
    for event in event_notifications_getter:
        participating = False
        for participant in EventParticipants.objects.filter(event=event):
            if participant.student == request.user:
                participating = True
                break
            else:
                continue
        if not participating:
            event_notifications.append(event)
    unregistered_events_count = len(event_notifications)

    return render(
        request,
        "cleanup-progress.html",
        {
            "school": school,
            "events": events,
            "participants": event_participants,
            "waste": waste,
            "events_held": Events.objects.filter(organised_by=school).count(),
            "rank": rank,
            "unregistered_events" : event_notifications,
            "unregistered_events_count" : unregistered_events_count
        },
    )


def ai_chat(request):
    if not request.user.is_authenticated:
        return redirect("login")
    event_notifications_getter = Events.objects.filter(date__gt = timezone.now().date())
    events = []
    for event in event_notifications_getter:
        participating = False
        for participant in EventParticipants.objects.filter(event=event):
            if participant.student == request.user:
                participating = True
                break
            else:
                continue
        if not participating:
            events.append(event)
    unregistered_events_count = len(events)
    return render(request, "chat.html", {"unregistered_events" : events,
            "unregistered_events_count" : unregistered_events_count})


def your_school(request):
    if not request.user.is_authenticated:
        return redirect("login")
    school = Student.objects.get(student=request.user).school
    event_notifications_getter = Events.objects.filter(date__gt = timezone.now().date())
    events = []
    for event in event_notifications_getter:
        participating = False
        for participant in EventParticipants.objects.filter(event=event):
            if participant.student == request.user:
                participating = True
                break
            else:
                continue
        if not participating:
            events.append(event)
    unregistered_events_count = len(events)
    return render(request, "your-school.html", {"school": school, "unregistered_events" : events,
            "unregistered_events_count" : unregistered_events_count})


def school_admin(request, active_tab="details"):
    if not request.user.is_authenticated:
        return redirect("login")

    is_admin = School.objects.filter(admin=request.user).exists()
    admin_school = None
    events_list = None
    if is_admin:
        admin_school = School.objects.filter(admin=request.user).first()
        events_list = Events.objects.filter(organised_by=admin_school)

        for event in events_list:
            event_datetime = datetime.combine(
                event.date, event.time
            )  # merge into datetime
            event_datetime = timezone.make_aware(
                event_datetime
            )  # make it timezone-aware

            if event_datetime < timezone.now():
                event.status = "completed"
            else:
                event.status = "upcoming"

        if request.method == "POST":
            if "create_event" in request.POST:
                event_title = request.POST["title"]
                event_date = request.POST["date"]
                event_time = request.POST["time"]
                event_location = request.POST["location"]
                expected_participants = request.POST["expected_participants"]
                event_type = request.POST["event_type"]
                event_description = request.POST["description"]
                event_requirements = request.POST["requirements"]
                Events.objects.create(
                    name=event_title,
                    description=event_description,
                    requirements=event_requirements,
                    event_type=event_type,
                    location=event_location,
                    date=event_date,
                    time=event_time,
                    expected_participants=expected_participants,
                    organised_by=admin_school,
                )
                messages.success(request, "Event Created Successfully 😤")
                return redirect("school_admin", "events")
            if "school_update" in request.POST:
                school_name = request.POST["name"]
                adopted_section = request.POST["adopted_section"]
                no_of_students = request.POST["no_of_students"]
                coordinate1_lat = request.POST["coordinate1_lat"]
                coordinate1_lng = request.POST["coordinate1_lng"]
                coordinate2_lat = request.POST["coordinate2_lat"]
                coordinate2_lng = request.POST["coordinate2_lng"]
                coordinate3_lat = request.POST["coordinate3_lat"]
                coordinate3_lng = request.POST["coordinate3_lng"]
                coordinate4_lat = request.POST["coordinate4_lat"]
                coordinate4_lng = request.POST["coordinate4_lng"]
                admin_school.name = school_name
                admin_school.adopted_section = adopted_section
                admin_school.no_of_students = no_of_students
                admin_school.coordinate1_lat = coordinate1_lat
                admin_school.coordinate1_lng = coordinate1_lng
                admin_school.coordinate2_lat = coordinate2_lat
                admin_school.coordinate2_lng = coordinate2_lng
                admin_school.coordinate3_lat = coordinate3_lat
                admin_school.coordinate3_lng = coordinate3_lng
                admin_school.coordinate4_lat = coordinate4_lat
                admin_school.coordinate4_lng = coordinate4_lng
                admin_school.save()
                messages.success(request, "School Details Updated Successfully 😤")
                return redirect("school_admin", "details")
            if "delete_event" in request.POST:
                event_id = request.POST["event_id"]
                Events.objects.get(id=event_id).delete()
                messages.success(request, "You deleted the event 🥲")
                return redirect("school_admin", "events")
            if "update_event" in request.POST:
                event_title = request.POST["title"]
                event_date = request.POST["date"]
                event_time = request.POST["time"]
                event_location = request.POST["location"]
                expected_participants = request.POST["expected_participants"]
                event_type = request.POST["event_type"]
                event_description = request.POST["description"]
                event_requirements = request.POST["requirements"]
                event_id = request.POST["event_id"]
                event = Events.objects.get(id=event_id)
                event.name = event_title
                event.description = event_description
                event.requirements = event_requirements
                event.date = event_date
                event.time = event_time
                event.expected_participants = expected_participants
                event.event_type = event_type
                event.location = event_location
                event.save()
                messages.success(request, "Event Details Updated Successfully 😤")
                return redirect("school_admin", "events")
            if "update_progress" in request.POST:
                waste_collected = request.POST["garbage"]
                plastic_collected = request.POST["plastic"]
                paper_collected = request.POST["paper"]
                glass_collected = request.POST["glass"]
                miscellaneous_collected = request.POST["miscellaneous"]
                event_id = request.POST["event_id"]
                update_event = Events.objects.get(id=event_id)
                update_event.waste_collected = waste_collected
                update_event.plastic_collected = plastic_collected
                update_event.paper_collected = paper_collected
                update_event.glass_collected = glass_collected
                update_event.miscellaneous_collected = miscellaneous_collected
                update_event.save()
                messages.success(request, "successfully updated event progress 😤")
                return redirect("school_admin", "events")
    
    event_notifications_getter = Events.objects.filter(date__gt = timezone.now().date())
    events = []
    for event in event_notifications_getter:
        participating = False
        for participant in EventParticipants.objects.filter(event=event):
            if participant.student == request.user:
                participating = True
                break
            else:
                continue
        if not participating:
            events.append(event)
    unregistered_events_count = len(events)

    return render(
        request,
        "admin.html",
        {
            "is_admin": is_admin,
            "active_tab": active_tab,
            "school": admin_school,
            "events": events_list,
            "unregistered_events" : events,
            "unregistered_events_count" : unregistered_events_count
        },
    )


def event_page(request, event_id):
    event = Events.objects.get(id=event_id)
    starting_time = datetime.combine(event.date, event.time)
    starting_time = timezone.make_aware(starting_time, timezone.get_current_timezone())
    is_expired=False
    if starting_time <= timezone.now():
        is_expired = True
    participants = EventParticipants.objects.filter(event=event)
    if participants.count() >= event.expected_participants:
        housefull = True
    else:
        housefull = False
    if EventParticipants.objects.filter(student=request.user, event=event).exists():
        already_registered = True
    else:
        already_registered = False
    if not already_registered:
        if request.method == "POST":
            event = EventParticipants.objects.create(student=request.user, event=event)
            return redirect("event_page", event_id)
    event_notifications_getter = Events.objects.filter(date__gt = timezone.now().date())
    events = []
    for notification_event in event_notifications_getter:
        participating = False
        for participant in EventParticipants.objects.filter(event=notification_event):
            if participant.student == request.user:
                participating = True
                break
            else:
                continue
        if not participating:
            events.append(notification_event)
    unregistered_events_count = len(events)
    return render(
        request,
        "event-page.html",
        {
            "event": event,
            "already_registered": already_registered,
            "participants": participants,
            "housefull": housefull,
            "unregistered_events" : events,
            "unregistered_events_count" : unregistered_events_count,
            "is_expired" : is_expired
        },
    )
