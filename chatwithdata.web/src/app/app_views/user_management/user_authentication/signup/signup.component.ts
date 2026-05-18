import { Component, AfterViewInit, ViewChild, ElementRef, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../app_services/auth.service';
import { ToastService } from '../../../../app_services/toast';
import intlTelInput from 'intl-tel-input';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule]
})

export class SignupComponent implements AfterViewInit {
  @ViewChild('phoneInput') phoneInputRef!: ElementRef;
  @ViewChild('genderContainer') genderContainer!: ElementRef;
  private iti: any;
  signupForm: FormGroup;
  showPassword = false;
  showConfirmPassword = false;
  isSubmitting = false;
  isGenderDropdownOpen = false;

  @HostListener('document:click', ['$event'])
  onClickOutside(event: Event) {
    if (this.genderContainer && !this.genderContainer.nativeElement.contains(event.target)) {
      this.isGenderDropdownOpen = false;
    }
  }

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService,
    private toastService: ToastService
  ) {
    this.signupForm = this.fb.group({
      firstName: ['', [Validators.required]],
      lastName: ['', [Validators.required]],
      gender: ['', [Validators.required]],
      phone: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, this.passwordStrengthValidator]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  // Getters for form controls
  get firstName() { return this.signupForm.get('firstName'); }
  get lastName() { return this.signupForm.get('lastName'); }
  get gender() { return this.signupForm.get('gender'); }
  get phone() { return this.signupForm.get('phone'); }
  get email() { return this.signupForm.get('email'); }
  get password() { return this.signupForm.get('password'); }
  get confirmPassword() { return this.signupForm.get('confirmPassword'); }

  ngAfterViewInit() {
    // Initialize intl-tel-input
    if (this.phoneInputRef) {
      this.iti = intlTelInput(this.phoneInputRef.nativeElement, {
        initialCountry: 'pk',
        separateDialCode: true,
        utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@23.0.12/build/js/utils.js'
      } as any);
    }
  }

  // Password strength validator
  passwordStrengthValidator(control: AbstractControl): ValidationErrors | null {
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

  // Password match validator
  passwordMatchValidator(group: AbstractControl): ValidationErrors | null {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;

    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  onSubmit() {
    if (this.signupForm.invalid) {
      Object.keys(this.signupForm.controls).forEach(key => {
        this.signupForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.isSubmitting = true;
    const formData = this.signupForm.value;

    // Extract phone number from intl-tel-input
    // If iti.getNumber() returns empty, fallback to formData.phone
    let phoneNumber: string | null = '';
    if (this.iti) {
      const itiNumber = this.iti.getNumber();
      phoneNumber = itiNumber || formData.phone;  // Use formData.phone if iti returns empty
    } else {
      phoneNumber = formData.phone;
    }

    // If phone number is empty string, set to null
    if (!phoneNumber || phoneNumber.trim() === '') {
      phoneNumber = null;
    }

    const apiData = {
      first_name: formData.firstName?.trim(),
      last_name: formData.lastName?.trim(),
      email: formData.email?.trim(),
      phone_number: phoneNumber ? phoneNumber.trim() : null, // Ensure phone number is trimmed
      gender: formData.gender,
      password: formData.password,
      device_id: this.authService.getDeviceId()
    };

    // Debug: Log the data being sent
    console.log('Registration API Data:', apiData);
    console.log('Password length:', formData.password?.length);

    this.authService.register(apiData).subscribe({
      next: (response) => {
        this.isSubmitting = false;
        this.toastService.show('Registration successful! Please sign in.', 'success');
        this.router.navigate(['/authentication/signin']);
      },
      error: (err) => {
        this.isSubmitting = false;
        console.error('Signup error:', err);
        console.error('Error details:', err.error);
        const errorMsg = err.error?.detail || err.error?.message || 'Registration failed. Please try again.';
        this.toastService.show(errorMsg, 'error');
      }
    });
  }

  toggleGenderDropdown() {
    this.isGenderDropdownOpen = !this.isGenderDropdownOpen;
  }

  selectGender(gender: string) {
    this.signupForm.patchValue({ gender });
    this.isGenderDropdownOpen = false;
  }
}
