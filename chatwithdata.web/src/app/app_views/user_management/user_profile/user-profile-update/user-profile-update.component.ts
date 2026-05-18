import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../../../app_services/auth.service';
import Swal from 'sweetalert2';
import { ApplicationConfiguration } from '../../../../app.config';
import { ImageCropperComponent, ImageCroppedEvent, LoadedImage } from 'ngx-image-cropper';
import { DomSanitizer } from '@angular/platform-browser';
import intlTelInput from 'intl-tel-input';

@Component({
  selector: 'user-profile-update',
  templateUrl: './user-profile-update.component.html',
  styleUrl: './user-profile-update.component.css',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ImageCropperComponent],
})
export class UserProfileUpdateComponent implements OnInit, AfterViewInit {
  @ViewChild('phoneInput') phoneInputRef!: ElementRef;
  @ViewChild('genderContainer') genderContainer!: ElementRef;
  private iti: any;
  profileForm: FormGroup;
  isLoading = false;

  @HostListener('document:click', ['$event'])
  onClickOutside(event: Event) {
    if (this.genderContainer && !this.genderContainer.nativeElement.contains(event.target)) {
      this.isGenderDropdownOpen = false;
    }
  }
  selectedFile: File | null = null;
  imagePreview: string | null = null;
  userInitials = '';

  // Image cropper properties
  imageChangedEvent: any = '';
  croppedImage: any = '';
  showCropper = false;

  genders = ['Male', 'Female', 'Other', 'Prefer not to say'];
  isGenderDropdownOpen = false;

  constructor(
    private fb: FormBuilder,
    public authService: AuthService,
    private sanitizer: DomSanitizer
  ) {
    this.profileForm = this.fb.group({
      first_name: [{ value: '', disabled: true }, Validators.required],
      last_name: [{ value: '', disabled: true }, Validators.required],
      phone: ['', Validators.required],
      gender: ['Other']
    });
    this.userInitials = this.authService.getUserInitials();
  }

  ngOnInit() {
    this.loadProfile();
  }

  ngAfterViewInit() {
    // Initialize intl-tel-input after view is ready
    setTimeout(() => {
      if (this.phoneInputRef) {
        this.iti = intlTelInput(this.phoneInputRef.nativeElement, {
          initialCountry: 'pk',
          separateDialCode: true,
          utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@23.0.12/build/js/utils.js'
        } as any);

        console.log('intl-tel-input initialized:', this.iti);

        // If phone value already exists in form, set it in intl-tel-input
        const currentPhone = this.profileForm.get('phone')?.value;
        if (currentPhone && this.iti) {
          this.iti.setNumber(currentPhone);
        }
      }
    }, 100);
  }

  loadProfile() {
    // Fetch complete user profile from API
    this.authService.getUserProfile().subscribe({
      next: (user) => {
        // Populate form with user data
        this.profileForm.patchValue({
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          phone: user.phone_number || '',
          gender: user.gender || 'Other'
        });

        // Set phone number in intl-tel-input if it's already initialized
        if (user.phone_number && this.iti) {
          setTimeout(() => {
            this.iti.setNumber(user.phone_number);
          }, 200);
        }

        // Load profile image if available
        if (user.profile_image_url) {
          const baseUrl = ApplicationConfiguration.Get().ServerBaseUrl;
          let fullUrl = user.profile_image_url;
          if (!fullUrl.startsWith('http')) {
            const relativePath = fullUrl.startsWith('/') ? fullUrl.substring(1) : fullUrl;
            fullUrl = `${baseUrl}/${relativePath}`;
          }

          this.imagePreview = fullUrl;
          this.authService.updateProfileImage(fullUrl);
        }
      },
      error: (err) => {
        console.error('Failed to load profile', err);
        // Fallback to localStorage data
        const name = this.authService.getUserName() || '';
        const parts = name.split(' ');
        this.profileForm.patchValue({
          first_name: parts[0] || '',
          last_name: parts.slice(1).join(' ') || '',
          phone: '',
          gender: 'Other'
        });

        const savedImage = this.authService.getUserProfileImage();
        if (savedImage) {
          this.imagePreview = savedImage;
        }
      }
    });
  }

  onFileSelected(event: any) {
    this.imageChangedEvent = event;
    this.showCropper = true;
    console.log('Cropper modal should show:', this.showCropper);
    console.log('Image event:', event);
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
  }

  imageCropped(event: ImageCroppedEvent) {
    // Only store the cropped blob, don't update preview yet
    this.croppedImage = event.blob;
  }

  imageLoaded(image: LoadedImage) {
    // Image loaded successfully
  }

  cropperReady() {
    // Cropper ready
  }

  loadImageFailed() {
    Swal.fire('Error', 'Failed to load image', 'error');
    this.showCropper = false;
  }

  applyCrop() {
    if (this.croppedImage) {
      // Convert blob to file
      const file = new File([this.croppedImage], 'profile.jpg', { type: 'image/jpeg' });
      this.selectedFile = file;

      // Create object URL for preview
      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);

      this.showCropper = false;

      // Restore body scroll
      document.body.style.overflow = '';

      Swal.fire({
        title: 'Image Ready',
        text: 'Click "Update Profile" to save changes',
        icon: 'info',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000
      });
    }
  }

  cancelCrop() {
    this.showCropper = false;
    this.imageChangedEvent = '';
    this.croppedImage = '';
    // Restore body scroll
    document.body.style.overflow = '';
  }

  onSubmit() {
    if (this.profileForm.valid) {
      this.isLoading = true;
      const data = this.profileForm.getRawValue();

      // Extract phone number from intl-tel-input
      console.log('ITI instance:', this.iti);
      console.log('Form phone value:', data.phone);
      console.log('Input element value:', this.phoneInputRef?.nativeElement?.value);

      let phoneNumber = null;

      if (this.iti) {
        // Try to get the number from intl-tel-input
        phoneNumber = this.iti.getNumber();
        console.log('Phone from iti.getNumber():', phoneNumber);

        // If getNumber() returns empty, try getting from the input element directly
        if (!phoneNumber || phoneNumber.trim() === '') {
          const inputValue = this.phoneInputRef?.nativeElement?.value;
          if (inputValue && inputValue.trim() !== '') {
            // Get the selected country data
            const countryData = this.iti.getSelectedCountryData();
            phoneNumber = `+${countryData.dialCode}${inputValue}`;
            console.log('Phone constructed from input:', phoneNumber);
          }
        }
      } else {
        // Fallback to form value if iti is not initialized
        phoneNumber = data.phone;
        console.log('Using form value (iti not initialized):', phoneNumber);
      }

      // If phone number is still empty or just whitespace, set to null
      if (!phoneNumber || phoneNumber.trim() === '') {
        phoneNumber = null;
        console.log('Phone number is empty, setting to null');
      }

      // Prepare API data with correct field names
      const apiData = {
        first_name: data.first_name,
        last_name: data.last_name,
        phone_number: phoneNumber,  // API expects 'phone_number', not 'phone'
        gender: data.gender,
        email: data.email  // Include email as well
      };

      console.log('Sending to API:', apiData);
      console.log('Phone number from intl-tel-input:', phoneNumber);

      const fullName = `${data.first_name} ${data.last_name}`;

      // First upload image if selected
      if (this.selectedFile) {
        this.authService.uploadProfileImage(this.selectedFile).subscribe({
          next: (res) => {
            // Image uploaded successfully
            if (res && res.profile_image_url) {
              const baseUrl = ApplicationConfiguration.Get().ServerBaseUrl;
              let fullUrl = res.profile_image_url;
              if (!fullUrl.startsWith('http')) {
                const relativePath = fullUrl.startsWith('/') ? fullUrl.substring(1) : fullUrl;
                fullUrl = `${baseUrl}/${relativePath}`;
              }

              this.authService.updateProfileImage(fullUrl);
              this.imagePreview = fullUrl;
            }

            // Now update profile data
            this.updateProfileData(apiData, fullName);
          },
          error: (err) => {
            this.isLoading = false;
            console.error('Upload failed', err);
            Swal.fire('Error', 'Failed to upload image', 'error');
          }
        });
      } else {
        // No image selected, just update profile data
        this.updateProfileData(apiData, fullName);
      }
    } else {
      this.profileForm.markAllAsTouched();
    }
  }

  updateProfileData(data: any, fullName: string) {
    this.authService.updateProfile(data).subscribe({
      next: (res) => {
        this.isLoading = false;
        const token = this.authService.getToken();
        if (token) this.authService.saveTokens(token, '', fullName);

        // Clear selected file after successful update
        this.selectedFile = null;

        Swal.fire('Success', 'Profile updated successfully', 'success');
      },
      error: (err) => {
        this.isLoading = false;
        Swal.fire('Error', 'Failed to update profile', 'error');
      }
    });
  }

  toggleGenderDropdown() {
    this.isGenderDropdownOpen = !this.isGenderDropdownOpen;
  }

  selectGender(gender: string) {
    this.profileForm.patchValue({ gender });
    this.isGenderDropdownOpen = false;
  }
}

