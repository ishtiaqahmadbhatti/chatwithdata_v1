import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import Swal from 'sweetalert2';
import { AuthService } from '../../../../app_services/auth.service';

@Component({
    selector: 'app-reset-password',
    templateUrl: './reset-password.component.html',
    styleUrl: './reset-password.component.css',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
})
export class ResetPasswordComponent implements OnInit {
    resetForm: FormGroup;
    isSubmitting = false;
    showNewPassword = false;
    showConfirmPassword = false;
    resetToken = '';

    constructor(
        private fb: FormBuilder,
        private authService: AuthService,
        private router: Router,
        private route: ActivatedRoute
    ) {
        this.resetForm = this.fb.group({
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

    ngOnInit() {
        this.route.queryParams.subscribe(params => {
            this.resetToken = params['token'];
            if (!this.resetToken) {
                Swal.fire('Error', 'Invalid or missing reset token', 'error').then(() => {
                    this.router.navigate(['/authentication/forgotpassword']);
                });
            }
        });
    }

    passwordMatchValidator(form: FormGroup) {
        return form.get('newPassword')?.value === form.get('confirmPassword')?.value
            ? null : { mismatch: true };
    }

    toggleVisibility(field: string) {
        if (field === 'new') this.showNewPassword = !this.showNewPassword;
        if (field === 'confirm') this.showConfirmPassword = !this.showConfirmPassword;
    }

    onSubmit() {
        if (this.resetForm.valid && this.resetToken) {
            this.isSubmitting = true;
            const newPassword = this.resetForm.get('newPassword')?.value;

            this.authService.resetPassword({ reset_token: this.resetToken, new_password: newPassword }).subscribe({
                next: (res) => {
                    this.isSubmitting = false;

                    Swal.fire({
                        title: 'Password Reset!',
                        text: res.message || 'Your password has been successfully reset. You can now login.',
                        icon: 'success',
                        confirmButtonColor: '#667eea'
                    }).then(() => {
                        this.authService.logout();
                        this.router.navigate(['/authentication/signin']);
                    });
                },
                error: (err) => {
                    this.isSubmitting = false;
                    this.handleError(err.error?.detail || err.error?.message || 'Failed to reset password');
                }
            });
        } else {
            this.resetForm.markAllAsTouched();
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
