from movies import notifications
from movies.models import MovieNightInvitation
from celery import shared_task

@shared_task
def send_invitation(mni_pk):
    notifications.send_invitation(MovieNightInvitation.objects.get(pk=mni_pk))

@shared_task
def send_attendance_change(mni_pk, is_attending):
    notifications.send_attendance_change(
        MovieNightInvitation.objects.get(pk=mni_pk), is_attending
    )

@shared_task
def notify_of_starting_soon():
    notifications.notify_of_starting_soon()
