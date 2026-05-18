import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastService } from '../../app_services/toast';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './toast.html',
  styleUrl: './toast.css',
})
export class ToastComponent { // Renamed to ToastComponent for clarity (though generic name was Toast)
  // Actually, keeping the class name consistent with usage might be better, 
  // but CLI named it Toast. Let's rename it to ToastComponent to follow convention if importable.
  // Wait, if I rename it here, I must update usage everywhere.

  constructor(public toastService: ToastService) { }

  remove(id: number) {
    this.toastService.remove(id);
  }
}
