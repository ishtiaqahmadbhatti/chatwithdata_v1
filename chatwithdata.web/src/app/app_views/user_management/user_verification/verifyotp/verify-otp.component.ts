import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import Swal from 'sweetalert2';
import { AuthService } from '../../../../app_services/auth.service';

@Component({
    selector: 'app-verify-otp',
    templateUrl: './verify-otp.component.html',
    styleUrl: './verify-otp.component.css',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, RouterModule],
})
export class VerifyOtpComponent implements OnInit, OnDestroy {
    otpForm: FormGroup;
    isSubmitting = false;
    email = '';

    // Timer
    timer: any;
    timeLeft = 180; // 3 minutes

    constructor(
        private fb: FormBuilder,
        private authService: AuthService,
        private router: Router,
        private route: ActivatedRoute
    ) {
        this.otpForm = this.fb.group({
            otp: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(6), Validators.pattern('^[0-9]+$')]]
        });
    }

    ngOnInit() {
        // Get email from query params or router state
        this.route.queryParams.subscribe(params => {
            this.email = params['email'];
            if (!this.email) {
                // Check state
                const nav = this.router.getCurrentNavigation();
                if (nav?.extras?.state) {
                    this.email = nav.extras.state['email'];
                }
            }

            if (!this.email) {
                Swal.fire('Error', 'No email provided for verification', 'error').then(() => {
                    this.router.navigate(['/authentication/forgotpassword']);
                });
                return;
            }

            this.startTimer();
        });
    }

    ngOnDestroy() {
        this.stopTimer();
    }

    onOtpSubmit() {
        if (this.otpForm.valid) {
            this.isSubmitting = true;
            const otp = this.otpForm.get('otp')?.value;

            this.authService.verifyOtp(this.email, otp).subscribe({
                next: (res) => {
                    this.isSubmitting = false;
                    // Check for token existence which is required for next step
                    if (res.reset_token) {
                        // Navigate to Reset Password
                        this.router.navigate(['/authentication/resetpassword'], {
                            queryParams: { token: res.reset_token }
                        });
                    } else {
                        // If 200 OK but no token, something is wrong with API response structure
                        this.handleError(res.message || 'Verification successful but missing reset token');
                    }
                },
                error: (err) => {
                    this.isSubmitting = false;
                    this.handleError(err.error?.detail || err.error?.message || 'Invalid code');
                }
            });
        } else {
            this.otpForm.markAllAsTouched();
        }
    }

    resendCode() {
        this.isSubmitting = true;
        const deviceId = this.authService.getDeviceId();

        this.authService.sendOtp(this.email, deviceId).subscribe({
            next: (res) => {
                this.isSubmitting = false;
                this.timeLeft = 180;
                this.startTimer();
                Swal.fire({
                    title: 'Code Resent',
                    text: 'A new code has been sent to your email.',
                    icon: 'success',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000
                });
            },
            error: (res) => {
                this.isSubmitting = false;
                this.handleError('Failed to resend code');
            }
        })
    }

    startTimer() {
        this.stopTimer();
        this.timer = setInterval(() => {
            if (this.timeLeft > 0) {
                this.timeLeft--;
            } else {
                this.stopTimer();
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    get timerText(): string {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    handleError(msg: string) {
        Swal.fire({
            title: 'Error!',
            text: msg,
            icon: 'error',
            confirmButtonColor: '#e53e3e'
        });
    }

    changeEmail() {
        this.router.navigate(['/authentication/forgotpassword']);
    }
}
