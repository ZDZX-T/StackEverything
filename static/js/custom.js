// 解决Sortable.create在火狐浏览器上会打开新窗口的问题
document.body.ondrop = function(event) {
    event.preventDefault();
    event.stopPropagation();
}
