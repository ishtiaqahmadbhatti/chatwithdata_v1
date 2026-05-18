import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../app_services/auth.service';
import { ToastService } from '../../../../app_services/toast';
import { ApplicationConfiguration } from '../../../../app.config';

@Component({
  selector: 'app-signin',
  templateUrl: './signin.component.html',
  styleUrls: ['./signin.component.css'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule]
})
export class SigninComponent implements OnInit {
  signinForm: FormGroup;
  showPassword = false;
  isSubmitting = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService,
    private toastService: ToastService
  ) {
    this.signinForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      rememberMe: [false]
    });
  }

  ngOnInit() {
    // Check for saved credentials in localStorage
    const savedEmail = localStorage.getItem('remember_me_email');
    const savedPassword = localStorage.getItem('remember_me_password');
    
    if (savedEmail) {
      this.signinForm.patchValue({
        email: savedEmail,
        password: savedPassword || '',
        rememberMe: true
      });
    }
  }

  // Getters for form controls
  get email() { return this.signinForm.get('email'); }
  get password() { return this.signinForm.get('password'); }
  get rememberMe() { return this.signinForm.get('rememberMe'); }

  onSubmit() {
    if (this.signinForm.invalid) {
      // Mark all fields as touched to show validation errors
      Object.keys(this.signinForm.controls).forEach(key => {
        this.signinForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.isSubmitting = true;
    const { email, password, rememberMe } = this.signinForm.value;
    const credentials = { email, password };

    this.authService.login(credentials).subscribe({
      next: (response) => {
        this.isSubmitting = false;

        // Handle Remember Me logic
        if (rememberMe) {
          localStorage.setItem('remember_me_email', email);
          localStorage.setItem('remember_me_password', password);
        } else {
          localStorage.removeItem('remember_me_email');
          localStorage.removeItem('remember_me_password');
        }
        // Adjust based on actual API response structure. 
        // Mobile implies response has access_token and refresh_token directly.
        if (response && response.access_token) {
          // Construct full profile image URL if available
          let profileImageUrl = undefined;
          if (response.profile_image_url) {
            const baseUrl = ApplicationConfiguration.Get().ServerBaseUrl;
            profileImageUrl = response.profile_image_url;
            if (!profileImageUrl.startsWith('http')) {
              const relativePath = profileImageUrl.startsWith('/') ? profileImageUrl.substring(1) : profileImageUrl;
              profileImageUrl = `${baseUrl}/${relativePath}`;
            }
          }

          this.authService.saveTokens(
            response.access_token,
            response.refresh_token,
            response.full_name || 'User',
            credentials.email,
            profileImageUrl
          );

          // Immediately fetch user profile to load image in header
          this.authService.getUserProfile().subscribe({
            next: (user) => {
              if (user.profile_image_url) {
                const baseUrl = ApplicationConfiguration.Get().ServerBaseUrl;
                let fullUrl = user.profile_image_url;
                if (!fullUrl.startsWith('http')) {
                  const relativePath = fullUrl.startsWith('/') ? fullUrl.substring(1) : fullUrl;
                  fullUrl = `${baseUrl}/${relativePath}`;
                }
                this.authService.updateProfileImage(fullUrl);
              }
            },
            error: (err) => console.error('Failed to load profile after login', err)
          });

          this.toastService.show('Sign in successful!', 'success');
          this.router.navigate(['/']);
        } else {
          console.error('Unexpected response structure:', response);
          this.toastService.show('Login succeeded but token missing. Please try again.', 'error');
        }
      },
      error: (err) => {
        this.isSubmitting = false;
        console.error('Signin error:', err);
        const errorMsg = err.error?.detail || err.error?.message || 'Sign in failed. Please check your credentials.';
        this.toastService.show(errorMsg, 'error');
      }
    });
  }
}
