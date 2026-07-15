from django.db import models
from django.conf import settings
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class QRCode(models.Model):
    """QR Code model"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='qr_codes'
    )
    
    till_id = models.CharField(max_length=20, unique=True, db_index=True)
    qr_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'qr_codes'
        indexes = [
            models.Index(fields=['till_id', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.till_id}"
    
    def generate_qr(self):
        """Generate QR code image"""
        data = f"ya://pay?tillid={self.till_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return ContentFile(buffer.getvalue(), f'qr_{self.till_id}.png')
