import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-jpg-to-avif',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './jpg-to-avif.component.html',
  styleUrl: './jpg-to-avif.component.css',
  standalone: true
})
export class JpgToAvifComponent extends BaseImageToolComponent {
  toolId = 'jpg-to-avif';
}
