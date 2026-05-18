import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './app_layouts/header/header.component';
import { FooterComponent } from './app_layouts/footer/footer.component';
import { ToastComponent } from './app_layouts/toast/toast';

import { AuthService } from './app_services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent, ToastComponent],
})
export class AppComponent implements OnInit {
  title = 'ChatWithData';

  constructor(private authService: AuthService) { }

  ngOnInit() {
    // Ensure we have a device ID and register as guest if typically valid
    // We do this every time to ensure the backend tracks this device presence or creates it
    this.authService.registerGuest().subscribe({
      next: () => console.log('Guest check/registration complete'),
      error: (err) => console.error('Guest check failed', err)
    });
  }
}