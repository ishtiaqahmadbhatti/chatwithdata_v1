import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const authService = inject(AuthService);
    const deviceId = authService.getDeviceId();
    const token = authService.getToken();

    let headers = req.headers.set('x-device-id', deviceId);

    if (token) {
        headers = headers.set('Authorization', `Bearer ${token}`);
    }

    const clonedReq = req.clone({
        headers: headers
    });

    return next(clonedReq);
};
