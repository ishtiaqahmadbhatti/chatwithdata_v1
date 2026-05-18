import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';
import { AuthService } from '../../../../app_services/auth.service';

@Component({
  selector: 'app-changepassword',
  templateUrl: './changepassword.component.html',
  styleUrl: './changepassword.component.css',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
})
export class ChangepasswordComponent {
  changePasswordForm: FormGroup;
  isSubmitting = false;
  showOldPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.changePasswordForm = this.fb.group({
      oldPassword: ['', Validators.required],
      newPassword: ['', [Validators.required, this.passwordStrengthValidator]],
      confirmPassword: ['', Validators.required]
    }, { validator: this.passwordMatchValidator });
  }

  passwordStrengthValidator(control: any) {
    const value = control.value;
    if (!value) return null;

    const hasUpperCase = /[A-Z]/.test(value);
    const hasLowerCase = /[a-z]/.test(value);
    const hasNumeric = /[0-9]/.test(value);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(value);
    const isLengthValid = value.length >= 8;

    const passwordValid = hasUpperCase && hasLowerCase && hasNumeric && hasSpecialChar && isLengthValid;

    return passwordValid ? null : { weakPassword: true };
  }

  passwordMatchValidator(form: FormGroup) {
    return form.get('newPassword')?.value === form.get('confirmPassword')?.value
      ? null : { mismatch: true };
  }

  toggleVisibility(field: string) {
    if (field === 'old') this.showOldPassword = !this.showOldPassword;
    if (field === 'new') this.showNewPassword = !this.showNewPassword;
    if (field === 'confirm') this.showConfirmPassword = !this.showConfirmPassword;
  }

  onSubmit() {
    if (this.changePasswordForm.valid) {
      this.isSubmitting = true;
      const { oldPassword, newPassword } = this.changePasswordForm.value;

      this.authService.changePassword({ old_password: oldPassword, new_password: newPassword })
        .subscribe({
          next: (res) => {
            this.isSubmitting = false;
            Swal.fire({
              title: 'Success!',
              text: 'Your password has been changed successfully. Please sign in again with your new password.',
              icon: 'success',
              confirmButtonColor: '#667eea'
            }).then(() => {
              this.authService.logout();
              this.router.navigate(['/authentication/signin']);
            });
          },
          error: (err) => {
            this.isSubmitting = false;
            console.error('Change password error:', err);
            Swal.fire({
              title: 'Error!',
              text: err.error?.detail || err.error?.message || 'Failed to change password. Please check your current password.',
              icon: 'error',
              confirmButtonColor: '#e53e3e'
            });
          }
        });
    } else {
      this.changePasswordForm.markAllAsTouched();
    }
  }
}
