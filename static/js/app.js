$(function() {
    function human(subject) {
        result = "";
        lowerDes = subject.description.toLowerCase();
        $.each(lowerDes.split(" "), function(i, part) {
            if(part)
                result += part[0].toUpperCase() + part.substring(1).toLowerCase() + " ";
        });
        result += "("+ subject.code+")";
        return result;
    }

    $('#subject').typeahead({
        source: function(part) {
            results = [];
            if($.isNumeric(part)) {
                $.each(subjects, function(i, subject) {
                    if(subject.code.indexOf(part) != -1) {
                        results.push(human(subject));
                    }
                });
            }
            else {
                $.each(subjects, function(i, subject) {
                    lowerDesc = subject.description.toLowerCase();
                    if(lowerDesc.indexOf(part.toLowerCase()) != -1)
                        results.push(human(subject));
                });
            }
            return results;
        }
    });

    $('#sniper-test').button().click(function() {
        var that = $(this);
        that.button('loading');
        $.ajax({
            url: '/test',
            success: function(response) {
                that.button('reset');
                if(response.success) {
                    alert('Yep looks to me like it does. Send me email at sniper@vverma.net if you think it doesn\'t.');
                } else {
                    alert('Looks like something\'s wrong. I\'ll work on fixing it asap.');
                }
            },
            dataType: 'json',
            error: function(response) {
                alert('Looks like something\'s wrong. I\'ll work on fixing it asap.');
            }
        });
    });
});
