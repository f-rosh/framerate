from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Circle(models.Model):
    GENRE = 'genre'
    DIRECTOR = 'director'
    ACTOR = 'actor'
    FRANCHISE = 'franchise'
    TOPIC_TYPES = [
        (GENRE, 'Genre'),
        (DIRECTOR, 'Director'),
        (ACTOR, 'Actor'),
        (FRANCHISE, 'Franchise'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(max_length=500, blank=True, default='')
    topic_type = models.CharField(max_length=20, choices=TOPIC_TYPES)
    topic_value = models.CharField(max_length=100)
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def founder_count(self):
        return self.memberships.filter(role=CircleMembership.FOUNDER).count()

    @property
    def member_count(self):
        return self.memberships.count()

    # 1-founder model: a circle is active as long as it has a founder.
    @property
    def is_active(self):
        return self.founder_count >= 1


class CircleMembership(models.Model):
    FOUNDER = 'founder'
    MEMBER = 'member'
    ROLE_CHOICES = [
        (FOUNDER, 'Founder'),
        (MEMBER, 'Member'),
    ]

    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='circle_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('circle', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.circle.name} ({self.role})"


# ===== Signals: lock a circle only if it loses ALL founders =====
# Under the 1-founder model this essentially never fires in normal use,
# but keeps the field meaningful if a founder is deleted via admin.

@receiver(post_save, sender=CircleMembership)
@receiver(post_delete, sender=CircleMembership)
def update_circle_lock_state(sender, instance, **kwargs):
    circle = instance.circle
    founder_count = CircleMembership.objects.filter(
        circle=circle, role=CircleMembership.FOUNDER
    ).count()

    if founder_count < 1 and not circle.is_locked:
        circle.is_locked = True
        circle.locked_at = timezone.now()
        circle.save(update_fields=['is_locked', 'locked_at'])
    elif founder_count >= 1 and circle.is_locked:
        circle.is_locked = False
        circle.locked_at = None
        circle.save(update_fields=['is_locked', 'locked_at'])
