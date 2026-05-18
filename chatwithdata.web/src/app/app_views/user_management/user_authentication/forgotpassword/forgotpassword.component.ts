import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import Swal from 'sweetalert2';
import { AuthService } from '../../../../app_services/auth.service';

@Component({
  selector: 'app-forgotpassword',
  templateUrl: './forgotpassword.component.html',
  styleUrl: './forgotpassword.component.css',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
})
export class ForgotpasswordComponent {
  isSubmitting = false;
  emailForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.emailForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  onEmailSubmit() {
    if (this.emailForm.valid) {
      this.isSubmitting = true;
      const email = this.emailForm.get('email')?.value;
      const deviceId = this.authService.getDeviceId();

      this.authService.sendOtp(email, deviceId).subscribe({
        next: (res) => {
          this.isSubmitting = false;

          Swal.fire({
            title: 'Code Sent!',
            text: res.message || `A verification code has been sent to ${email}`,
            icon: 'success',
            confirmButtonColor: '#667eea',
            timer: 2000
          }).then(() => {
            // Navigate to Verify OTP Page with email
            this.router.navigate(['/verification/verify-otp'], {
              queryParams: { email: email }
            });
          });
        },
        error: (err) => {
          this.isSubmitting = false;
          this.handleError(err.error?.detail || err.error?.message || 'Failed to send code');
        }
      });
    } else {
      this.emailForm.markAllAsTouched();
    }
  }

  handleError(msg: string) {
    Swal.fire({
      title: 'Error!',
      text: msg,
      icon: 'error',
      confirmButtonColor: '#e53e3e'
    });
  }
}
