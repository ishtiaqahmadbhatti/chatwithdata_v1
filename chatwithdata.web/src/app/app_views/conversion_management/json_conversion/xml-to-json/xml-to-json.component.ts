import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-xml-to-json',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './xml-to-json.component.html',
  styleUrl: './xml-to-json.component.css',
  standalone: true
})
export class XmlToJsonComponent extends BaseJsonToolComponent {
  toolId = 'xml-to-json';
}
