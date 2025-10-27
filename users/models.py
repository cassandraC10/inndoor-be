from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class UserProfile(models.Model):
	class Roles(models.TextChoices):
		TENANT = 'TENANT', 'Tenant'
		AGENT = 'AGENT', 'Agent'
		BOTH = 'BOTH', 'Both'

	class VerificationStatus(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		VERIFIED = 'VERIFIED', 'Verified'
		REJECTED = 'REJECTED', 'Rejected'

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.TENANT)
	phone_number = models.CharField(
		max_length=20,
		blank=True,
		help_text='Primary phone number',
		validators=[RegexValidator(r'^\+?\d{7,15}$', 'Enter a valid phone number.')],
	)
	profile_picture = models.ImageField(upload_to='profiles/%Y/%m/%d/', blank=True, null=True)
	bio = models.TextField(blank=True)
	verification_status = models.CharField(max_length=10, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
	is_verified = models.BooleanField(default=False, help_text='Quick boolean mirror of verification_status')
	verification_document = models.FileField(upload_to='verifications/%Y/%m/%d/', blank=True, null=True)
	total_listings = models.PositiveIntegerField(default=0)
	total_inspections = models.PositiveIntegerField(default=0)
	rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'user_profiles'

	def __str__(self):
		return f"{self.user.get_full_name() or self.user.username} ({self.role})"


class Property(models.Model):
	class PropertyType(models.TextChoices):
		APARTMENT = 'APARTMENT', 'Apartment'
		FLAT = 'FLAT', 'Flat'
		DUPLEX = 'DUPLEX', 'Duplex'
		ROOM = 'ROOM', 'Room'
		SELF_CONTAIN = 'SELF_CONTAIN', 'Self-contain'

	class Status(models.TextChoices):
		DRAFT = 'DRAFT', 'Draft'
		ACTIVE = 'ACTIVE', 'Active'
		RENTED = 'RENTED', 'Rented'
		EXPIRED = 'EXPIRED', 'Expired'

	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties', help_text='Original tenant who listed the property')
	title = models.CharField(max_length=255)
	description = models.TextField()
	property_type = models.CharField(max_length=20, choices=PropertyType.choices)
	address = models.CharField(max_length=500)
	city = models.CharField(max_length=100, db_index=True)
	state = models.CharField(max_length=100)
	landmark = models.CharField(max_length=255, blank=True)
	latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
	longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
	bedrooms = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0)])
	bathrooms = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0)])
	price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
	pros = models.TextField(blank=True, help_text="What's great about this place")
	cons = models.TextField(blank=True, help_text="What's not so great - honest tenant review")
	is_furnished = models.BooleanField(default=False)
	has_parking = models.BooleanField(default=False)
	pets_allowed = models.BooleanField(default=False)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT, db_index=True)
	available_from = models.DateField(blank=True, null=True)
	move_out_date = models.DateField(blank=True, null=True)
	commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, validators=[MinValueValidator(0), MaxValueValidator(100)])
	views_count = models.PositiveIntegerField(default=0)
	is_verified = models.BooleanField(default=False)
	verified_at = models.DateTimeField(blank=True, null=True)
	verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='verified_properties', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'properties'
		ordering = ['-created_at']
		verbose_name_plural = 'Properties'

	def __str__(self):
		return f"{self.title} - {self.city} ({self.status})"


class PropertyImage(models.Model):
	property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
	image = models.ImageField(upload_to='properties/%Y/%m/%d/')
	caption = models.CharField(max_length=255, blank=True)
	is_primary = models.BooleanField(default=False)
	order = models.PositiveIntegerField(default=0)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'property_images'
		ordering = ['order', '-is_primary']

	def __str__(self):
		return f"Image for {self.property.title} (primary={self.is_primary})"


class Inspection(models.Model):
	class Status(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		CONFIRMED = 'CONFIRMED', 'Confirmed'
		COMPLETED = 'COMPLETED', 'Completed'
		CANCELLED = 'CANCELLED', 'Cancelled'
		NO_SHOW = 'NO_SHOW', 'No show'

	property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inspections')
	requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inspection_requests')
	agent = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_inspections', blank=True, null=True)
	preferred_date = models.DateField()
	preferred_time = models.TimeField()
	confirmed_datetime = models.DateTimeField(blank=True, null=True)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
	requester_notes = models.TextField(blank=True)
	agent_notes = models.TextField(blank=True)
	confirmed_by_tenant = models.BooleanField(default=False)
	confirmed_by_agent = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'inspections'

	def __str__(self):
		return f"Inspection for {self.property.title} by {self.requester.username} on {self.preferred_date} {self.preferred_time}"


class Deal(models.Model):
	class Status(models.TextChoices):
		INITIATED = 'INITIATED', 'Initiated'
		PENDING_PAYMENT = 'PENDING_PAYMENT', 'Pending payment'
		PAID = 'PAID', 'Paid'
		COMPLETED = 'COMPLETED', 'Completed'
		CANCELLED = 'CANCELLED', 'Cancelled'

	property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='deals')
	tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deals_as_tenant')
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deals_as_owner')
	agent = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='deals_as_agent', blank=True, null=True)
	rent_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
	commission_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
	owner_commission = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
	agent_commission = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
	lease_start_date = models.DateField(blank=True, null=True)
	lease_end_date = models.DateField(blank=True, null=True)
	payment_reference = models.CharField(max_length=255, blank=True)
	paid_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'deals'

	def __str__(self):
		return f"Deal {self.id} - {self.property.title} ({self.status})"


class Review(models.Model):
	class ReviewType(models.TextChoices):
		PROPERTY = 'PROPERTY', 'Property'
		USER = 'USER', 'User'

	reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
	review_type = models.CharField(max_length=10, choices=ReviewType.choices)
	property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews', blank=True, null=True)
	reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews', blank=True, null=True)
	rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
	title = models.CharField(max_length=255, blank=True)
	comment = models.TextField()
	is_verified_stay = models.BooleanField(default=False)
	is_flagged = models.BooleanField(default=False)
	flag_reason = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'reviews'
		constraints = [
			models.UniqueConstraint(fields=['reviewer', 'property'], name='unique_reviewer_property', condition=models.Q(property__isnull=False)),
			models.UniqueConstraint(fields=['reviewer', 'reviewed_user'], name='unique_reviewer_user', condition=models.Q(reviewed_user__isnull=False)),
		]

	def __str__(self):
		target = self.property.title if self.review_type == self.ReviewType.PROPERTY and self.property else (self.reviewed_user.username if self.reviewed_user else 'Unknown')
		return f"Review by {self.reviewer.username} - {target} ({self.rating})"


class Message(models.Model):
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
	property = models.ForeignKey(Property, on_delete=models.SET_NULL, related_name='messages', blank=True, null=True)
	content = models.TextField()
	attachment = models.FileField(upload_to='messages/attachments/%Y/%m/%d/', blank=True, null=True)
	is_read = models.BooleanField(default=False)
	read_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'messages'

	def __str__(self):
		return f"Message from {self.sender.username} to {self.recipient.username} ({'read' if self.is_read else 'unread'})"


class Notification(models.Model):
	class NotificationType(models.TextChoices):
		INSPECTION_REQUEST = 'INSPECTION_REQUEST', 'Inspection Request'
		INSPECTION_CONFIRMED = 'INSPECTION_CONFIRMED', 'Inspection Confirmed'
		MESSAGE_RECEIVED = 'MESSAGE_RECEIVED', 'Message Received'
		DEAL_INITIATED = 'DEAL_INITIATED', 'Deal Initiated'
		PAYMENT_RECEIVED = 'PAYMENT_RECEIVED', 'Payment Received'
		REVIEW_RECEIVED = 'REVIEW_RECEIVED', 'Review Received'
		PROPERTY_VERIFIED = 'PROPERTY_VERIFIED', 'Property Verified'

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
	notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
	title = models.CharField(max_length=255)
	message = models.TextField()
	related_property = models.ForeignKey(Property, on_delete=models.SET_NULL, related_name='+', blank=True, null=True)
	related_inspection = models.ForeignKey(Inspection, on_delete=models.SET_NULL, related_name='+', blank=True, null=True)
	related_deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, related_name='+', blank=True, null=True)
	is_read = models.BooleanField(default=False)
	read_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'notifications'

	def __str__(self):
		return f"Notification for {self.user.username}: {self.title}"


class SavedProperty(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_properties')
	property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='saved_by')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'saved_properties'
		constraints = [models.UniqueConstraint(fields=['user', 'property'], name='unique_user_saved_property')]

	def __str__(self):
		return f"{self.user.username} saved {self.property.title}"

