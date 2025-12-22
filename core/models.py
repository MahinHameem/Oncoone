from django.db import models


class Registration(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField()
	contact = models.CharField(max_length=50)
	course = models.CharField(max_length=255)
	auto_bridge = models.BooleanField(default=False)
	# keep FileField for compatibility, but also store file bytes in DB for small-scale projects
	proof = models.FileField(upload_to='proofs/', blank=True, null=True)
	# DB storage fields
	proof_name = models.CharField(max_length=255, blank=True, null=True)
	proof_mime = models.CharField(max_length=100, blank=True, null=True)
	proof_data = models.BinaryField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.name} <{self.email}> - {self.course}"
