import { Component, HostListener, OnInit, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RouterModule } from '@angular/router';
import { AuthService } from '../../app_services/auth.service';
import { ApplicationConfiguration } from '../../app.config';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrl: './header.component.css',
  standalone: true,
  imports: [CommonModule, RouterModule]
})

export class HeaderComponent implements OnInit {
  isScrolled = false;
  isMobileMenuOpen = false;
  showDropdown = false;
  showProfileDropdown = false;

  tools = [
    { name: 'PDF Conversion Tools', icon: 'fas fa-file-pdf', link: '/pdfconversion', type: 'route' },
    { name: 'Office Conversion Tools', icon: 'fas fa-file-word', link: '/officeconversion', type: 'route' },
    { name: 'Image Conversion Tools', icon: 'fas fa-image', link: '/imageconversion', type: 'route' },
    { name: 'Video Conversion Tools', icon: 'fas fa-video', link: '/videoconversion', type: 'route' },
    { name: 'Audio Conversion Tools', icon: 'fas fa-music', link: '/audioconversion', type: 'route' },
    { name: 'JSON Conversion Tools', icon: 'fas fa-database', link: '/jsonconversion', type: 'route' },
    { name: 'XML Conversion Tools', icon: 'fas fa-code', link: '/xmlconversion', type: 'route' },
    { name: 'CSV Conversion Tools', icon: 'fas fa-table', link: '/csvconversion', type: 'route' },
    { name: 'OCR Conversion Tools', icon: 'fas fa-file-alt', link: '/ocrconversion', type: 'route' },
    { name: 'Website Conversion Tools', icon: 'fas fa-globe', link: '/websiteconversion', type: 'route' },
    { name: 'Subtitle Conversion Tools', icon: 'fas fa-closed-captioning', link: '/subtitleconversion', type: 'route' },
    { name: 'Markdown Conversion Tools', icon: 'fab fa-markdown', link: '/markdownconversion', type: 'route' },
    { name: 'Text Conversion Tools', icon: 'fas fa-font', link: '/textconversion', type: 'route' },
    { name: 'E-Book Conversion Tools', icon: 'fas fa-book', link: '/ebookconversion', type: 'route' },
    { name: 'File Formatter Tools', icon: 'fas fa-wrench', link: '/fileformatter', type: 'route' }
  ];

  constructor(public authService: AuthService, private eRef: ElementRef) { }

  @HostListener('document:click', ['$event'])
  clickout(event: any) {
    if (!this.eRef.nativeElement.contains(event.target)) {
      this.isMobileMenuOpen = false;
      this.showDropdown = false;
      this.showProfileDropdown = false;
    }
  }

  ngOnInit() {
    // Load user profile image from database if logged in
    if (this.authService.isLoggedIn()) {
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
        error: (err) => {
          console.error('Failed to load user profile in header', err);
        }
      });
    }
  }

  @HostListener('window:scroll', [])
  onWindowScroll() {
    this.isScrolled = window.scrollY > 50;
  }

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  logout() {
    this.authService.logout();
    this.showProfileDropdown = false;
    this.isMobileMenuOpen = false;
  }
}
