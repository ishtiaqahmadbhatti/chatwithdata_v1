import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-avif-to-webp',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './avif-to-webp.component.html',
  styleUrl: './avif-to-webp.component.css',
  standalone: true
})
export class AvifToWebpComponent extends BaseImageToolComponent {
  toolId = 'avif-to-webp';
}
