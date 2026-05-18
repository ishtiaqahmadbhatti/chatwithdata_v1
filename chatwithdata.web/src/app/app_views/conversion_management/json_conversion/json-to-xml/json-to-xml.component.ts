import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-json-to-xml',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-to-xml.component.html',
  styleUrl: './json-to-xml.component.css',
  standalone: true
})
export class JsonToXmlComponent extends BaseJsonToolComponent {
  toolId = 'json-to-xml';
}
