#include <curl.h>

static inline CURLMcode acurl_multi_setopt_pointer(CURLM * multi_handle, CURLMoption option, void * param) {
  return curl_multi_setopt(multi_handle, option, param);
}

static inline CURLMcode acurl_multi_setopt_socketcb(CURLM * multi_handle, CURLMoption option, curl_socket_callback param) {
  return curl_multi_setopt(multi_handle, option, param);
}

static inline CURLMcode acurl_multi_setopt_timercb(CURLM * multi_handle, CURLMoption option, curl_multi_timer_callback param) {
  return curl_multi_setopt(multi_handle, option, param);
}

static inline CURLMcode acurl_multi_setopt_long(CURLM * multi_handle, CURLMoption option, long param) {
  return curl_multi_setopt(multi_handle, option, param);
}

static inline CURLcode acurl_easy_getinfo_long(CURL *curl, CURLINFO info, long *data) {
  return curl_easy_getinfo(curl, info, data);
}

static inline CURLcode acurl_easy_getinfo_cstr(CURL *curl, CURLINFO info, char **data) {
  return curl_easy_getinfo(curl, info, data);
}

static inline CURLcode acurl_easy_getinfo_double(CURL *curl, CURLINFO info, double *data) {
  return curl_easy_getinfo(curl, info, data);
}

static inline CURLcode acurl_easy_getinfo_voidptr(CURL *curl, CURLINFO info, void *data) {
  // Curl technically uses char* instead of void*, but I fea that will confuse cython...
  return curl_easy_getinfo(curl, info, data);
}

static inline CURLSHcode acurl_share_setopt_int(CURLSH *share, CURLSHoption option, int data) {
  return curl_share_setopt(share, option, data);
}

static inline CURLcode acurl_easy_setopt_voidptr(CURL *easy, CURLoption option, void *data) {
  return curl_easy_setopt(easy, option, data)
}

static inline CURLcode acurl_easy_setopt_cstr(CURL *easy, CURLoption option, const char *data) {
  return curl_easy_setopt(easy, option, data)
}

static inline CURLcode acurl_easy_setopt_int(CURL *easy, CURLoption option, int data) {
  return curl_easy_setopt(easy, option, data)
}
