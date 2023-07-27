// Profile image upload
document.getElementById("profile_img").addEventListener("change", function () {
	document.getElementById("profile_img_placeholder").value = this.files[0].name;
});

// Banner image upload
document.getElementById("header_img").addEventListener("change", function () {
	document.getElementById("header_img_placeholder").value = this.files[0].name;
});

// Google Places Autocomplete initialization
function initAutocomplete() {
	new google.maps.places.Autocomplete(
		document.getElementById("location")
	);
}

window.onload = initAutocomplete;
