import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-png-to-jpg',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './png-to-jpg.component.html',
  styleUrl: './png-to-jpg.component.css',
  standalone: true
})
export class PngToJpgComponent extends BaseImageToolComponent {
  toolId = 'png-to-jpg';
}
