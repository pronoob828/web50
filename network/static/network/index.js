const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const Like_url = "static/images/Like_btn.png";
const Unlike_url = "static/images/Unlike_btn.png";
const comments_icon = "static/images/comment_icon.png";
var current_page = 1

// Hopefully the function names are self explanatory

document.addEventListener("DOMContentLoaded", function () {

    // For some reason the @login_required decorator isn't redirecting
    function redirect_to_login() {
        window.location.href = "/login"
    }


    // Returns a promise which contains true or false
    async function check_login() {
        const response = await fetch("/check_login")
        const data = await response.json()
        const logged_in = data["is_authenticated"]
        return logged_in
    }


    check_login().then(logged_in => {
        const create_post_btn = document.querySelector('#create_post_btn')
        create_post_btn.addEventListener('click', function () {

            // If a user is not logged in, and tries to create a post
            // They will be redirected to login page
            if (logged_in) {
                // Creating a post
                const post = document.querySelector('#create_post_text')
                fetch('/create_post', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrftoken },
                    body: JSON.stringify({
                        post_text: post.value,
                    })
                }).then(response => response.json())
                    .then(function () { load_posts(1) })

                post.value = '';
            } else {
                alert("You must be logged in to do that, redirecting now")
                redirect_to_login()
            }
        })
    })


    load_posts(current_page)


    // Well... it loads all the posts
    // TODO - Pagination
    function load_posts(page_no) {

        document.querySelector('#all_posts').innerHTML = `<h2 class='mt-3 mb-0'>All Posts</h2>(Page : ${current_page})`;
        fetch(`/show_posts/${page_no}`)
            .then(response => response.json())
            // Everything from here on out is inside this .then, 
            // TODO, figure out a way to clean this up if needed 
            .then(posts => {
                document.querySelector("#paginator").classList.remove("d-none")
                load_given_posts(posts, "all_posts", 0)
            })

    }


    function load_given_posts(posts, div_id, edit_index) {

        // Appending loaded posts to main div in index.html
        posts.forEach(post => {

            const post_container = document.createElement('div');
            // d stands for display so like_d means like button display
            // Both variables are added in classlist of like and unlike buttons
            if (post.liked) {
                var like_d = "d-none";
                var unlike_d = "";
            } else {
                var like_d = "";
                var unlike_d = "d-none";
            }
            var post_like_count = post.post_like_count
            var post_comment_count = post.post_comment_count
            var edit_btn = ""
            if (post.users_own_post) {
                edit_btn = `<span id="edit_post_${post.id}" class="click_exempt btn btn-primary edit_btns">Edit</span>`
            }

            post_container.innerHTML = `
        <div class="col-9">
        <h4><span id="username_${post.poster.id}" class="click_exempt username">${post.poster.username}</span></h4>
        <span id="post_content_${post.id}"><p>${post.post_body}</p></span>
        <span id="like_${post.id}" class="click_exempt mr-4 like_btns">
            <span id="like_btn" class="click_exempt ${like_d}"><img src="${Like_url}" class="click_exempt" alt="Like button" width=25px></span>
            <span id="unlike_btn" class="click_exempt ${unlike_d}"><img class="click_exempt" src="${Unlike_url}" alt="Unlike button" width=25px></span>
        </span>
        <span id="post_likes_${post.id}" class ="mr-4 post_likes">${post_like_count} Likes</span>
        <span id="post_comment_${post.id}" class="mr-4 comment_btn">${[post_comment_count]} Comments 
        <img src="${comments_icon}" width="20px"></span>
        `+ edit_btn + `
        </div>
        <span class="text-right col-3 text-muted">${post.post_add_time}</span>
        
                                `
            post_container.id = `post_${post.id}`
            post_container.classList = "post_container py-3 container-fluid d-flex border rounded my-1";
            document.querySelector(`#${div_id}`).append(post_container);

        });
        load_usernames()


        // Adding event listener to all posts in order to laod a specific post on click.
        const all_post_containers = document.querySelectorAll(".post_container");
        all_post_containers.forEach(container => {
            container.addEventListener("click", function load_post(e) {
                // Container id ends with post id ('post_${post.id}')
                var id = container.id.split("_")[1]
                // Clicking on the like button also triggered this, so if element has a src attribute, don't do anything 
                // TODO - Find better way to do this
                if ("click_exempt" == e.target.classList[0]) {
                    return
                }

                // Load single post
                fetch(`show_post/${id}`)
                    .then(response => response.json())
                    .then(post => {
                        document.querySelector("#show_post").innerHTML = ""

                        const post_container = document.createElement('div')
                        // d stands for display so unlike_d means unlike button display
                        // Both variables are added in classlist of like and unlike buttons
                        if (post.liked) {
                            var like_d = "d-none";
                            var unlike_d = "";
                        } else {
                            var like_d = "";
                            var unlike_d = "d-none";
                        }

                        // Generating single post html
                        var post_like_count = post.post_like_count
                        var post_comment_count = post.post_comment_count
                        var edit_btn = ""
                        if (post.users_own_post) {
                            edit_btn = `<span id="edit_open_post_${post.id}" class="click_exempt btn btn-primary edit_open_btns">Edit</span>`
                        }
                        post_container.innerHTML = `
                    
                    <div class="continer_fluid p-3">
                        <div class="text-center p-2">
                            <h2><span id="username_${post.poster.id}" class="click_exempt username">${post.poster.username}</span></h2>
                        </div>
                        <div class="text-center">
                            <small class="text-muted"><span class="mr-4">Added : ${post.post_add_time}</span> <span>Updated :
                                    ${post.post_update_time}</span></small>
                        </div>
                        <div id="open_post_content_${post.id}" class="text-center my-4">
                            <p class="text-center mb-5">${post.post_body}</p>
                        </div>
                        <div class="text-center">
                            <span id="like_${post.id}" class="mr-4 like_btns">
                                <span id="like_btn" class="${like_d}"><img src="${Like_url}" alt="Like button" width=25px></span>
                                <span id="unlike_btn" class="${unlike_d}"><img src="${Unlike_url}" alt="Unlike button" width=25px></span>
                            </span>
                            <span id="post_likes_${post.id}" class="mr-4 post_likes"><a href="#">${post_like_count} Likes</a></span>
                            `+ edit_btn + `
                        </div>
                    </div>
                    `

                        // Creating a container for all likes which is initially hidden 
                        // Max heigh of continer is 200px
                        const likes_container = document.createElement('div');
                        likes_container.id = `likes_container`
                        likes_container.classList = "d-none border container-fluid p-3";
                        likes_container.style = "max-height:200px;overflow:auto;"

                        // Filling the Likes container
                        post.post_likes.forEach(like => {
                            const like_container = document.createElement("div");
                            like_container.classList = "mx-auto container-fluid"
                            like_container.innerHTML = `
                        <span><img class="mr-3" src="${Unlike_url}" width="20px"><span id="username_${like.id}" class="click_exempt username">${like.username}</span></span>
                        `
                            likes_container.append(like_container)
                        })
                        post_container.append(likes_container)


                        // Creating the "Comments" heading
                        const comments_heading = document.createElement("div")
                        comments_heading.innerHTML =
                            `
                    <hr>
                    <h4>
                        <img src="${comments_icon}" width="30px"> Comments  (${post_comment_count})
                    </h4>
                    <hr>
                    <div class="container-fluid p-2 mb-2">
                        <h4>Post Comment</h4>
                        <textarea id="post_comment_text" required name="comment_body" cols="30" rows="5" placeholder="Your Comment..." class="form-control my-3"></textarea>
                        <button id="post_comment_btn" class="float-right btn btn-primary">Post</button>
                    </div>
                    <br>
                    <hr>
                    `
                        post_container.append(comments_heading)


                        // Loading comments
                        const comments_container = document.createElement("div")
                        load_comments()

                        // Its a bit too late to change this now but, every post is loaded with ALL of its comments,
                        // I didn't think of this back then but this is not good if we have a lot of comments on the post
                        // Lesson learned
                        function load_comments() {
                            // Getting post comments
                            const comments = post.post_comments
                            // Sorting by top liked
                            comments.sort(function (comment1, comment2) {
                                let cl1 = comment1.comment_like_count
                                let cl2 = comment2.comment_like_count
                                return (cl2 - cl1)
                            })
                            // Adding comments to comments container
                            comments.forEach(comment => {
                                if (comment.comment_is_liked == true) {
                                    var like_d = "d-none";
                                    var unlike_d = "";
                                } else {
                                    var like_d = "";
                                    var unlike_d = "d-none";
                                }
                                const comment_container = document.createElement('div')
                                comment_container.innerHTML = `
                        
                        <h4 class="mb-0"><span id="user_${comment.commenter.id}" class="click_exempt username">${comment.commenter.username}</span></h4>
                        <small class="text-muted mb-5 mt-0">commented</small>
                        <p class="my-1 mt-3 mb-3">${comment.comment_body}</p>

                        <span id="like_${comment.comment_id}" class="mr-4 comment_like_btns">
                            <span id="comment_like_btn" class="${like_d}"><img src="${Like_url}" alt="Like button" width=25px></span>
                            <span id="comment_unlike_btn" class="${unlike_d}"><img src="${Unlike_url}" alt="Unlike button" width=25px></span>
                        </span>

                        <span id="comment_likes_${comment.comment_id}" class="mr-4">${comment.comment_like_count} Likes</span>
                        <span class = "float-right text-muted">${comment.comment_add_time}</span>
                        
                        `
                                comment_container.classList = " border comment_container container-fluid p-2 my-1"
                                comment_container.id = `comment_${comment.comment_id}`
                                comments_container.append(comment_container)
                            })

                        }
                        // Adding comments to post's html
                        post_container.append(comments_container)

                        post_container.id = `post_${post.id}`
                        // Finally displaying the post
                        document.querySelector("#show_post").append(post_container)

                        add_comment_like_button()
                        // Adding like button to comments... pretty self explanatory
                        function add_comment_like_button() {
                            const comments = post.post_comments
                            const like_button = document.querySelectorAll(".comment_like_btns")
                            // Adding event listener for each like comment button in the document
                            like_button.forEach(button => {
                                const id = button.id.split('_')[1]
                                const comments_filtered = comments.filter(comment => comment["comment_id"] == id)
                                const comment = comments_filtered[0]


                                button.addEventListener("click", function () {
                                    check_login().then(logged_in => {
                                        // If user is not logged in , redirect to login page on click
                                        if (logged_in) {
                                            // set action tp ike or unlike depending on the situation
                                            if (comment.comment_is_liked) {
                                                var action = "unlike"
                                                comment.comment_is_liked = false
                                            } else {
                                                var action = "like"
                                                comment.comment_is_liked = true
                                            }
                                            var comment_div = document.querySelector(`#comment_${id}`)
                                            // Asks to like or unlike the comment depending on action specified
                                            fetch(`/like_comment/${id}`, {
                                                method: "PUT",
                                                headers: { 'X-CSRFToken': csrftoken },
                                                body: JSON.stringify({ action: action })
                                            }).then(function () {
                                                // Show relevant button
                                                button.querySelector("#comment_like_btn").classList.toggle("d-none");
                                                button.querySelector("#comment_unlike_btn").classList.toggle("d-none");

                                                fetch(`/get_comment_like_count/${id}`)
                                                    .then(response => response.json())
                                                    .then(data => {
                                                        var comment_like_count = data["like_count"]
                                                        comment_div.querySelector(`#comment_likes_${id}`).innerHTML = `${comment_like_count} Likes`
                                                    })
                                            })
                                        } else {
                                            alert("You must be logged in to do that")
                                            redirect_to_login()
                                        }
                                    })
                                })
                            })
                        }


                        // Clicking on like count will display all the likes the post has
                        const post_likes = document.querySelectorAll(`#post_likes_${post.id}`)[1];
                        post_likes.addEventListener("click", function () {
                            document.querySelector(`#likes_container`).classList.toggle("d-none")
                        })


                        const comment_btn = document.querySelector('#post_comment_btn')
                        // Posting comment, just a post request,
                        // If not logged in, redirect to login page onclick
                        comment_btn.addEventListener('click', function () {

                            check_login().then(logged_in => {

                                if (logged_in) {
                                    const comment = document.querySelector('#post_comment_text')
                                    fetch(`/post_comment/${post.id}`, {
                                        method: 'POST',
                                        headers: { 'X-CSRFToken': csrftoken },
                                        body: JSON.stringify({
                                            comment_text: comment.value
                                        })
                                    }).then(response => response.json())
                                    comment.value = '';

                                } else {
                                    alert("You must be logged in to do that")
                                    redirect_to_login()
                                }
                            })
                        })

                    }).then(function () {
                        // After loading post , show the post page and hide the all posts page
                        document.querySelector("#show_all_posts").classList.add("d-none")
                        document.querySelector("#show_post").classList.remove("d-none")
                        document.querySelector("#show_user_profile").classList.add("d-none")
                        add_like_buttons(1);

                    }).then(function () {

                        const edit_open_btns = document.querySelectorAll(".edit_open_btns")
                        edit_open_btns.forEach(btn => {
                            var counter = 0
                            btn.addEventListener("click", () => {
                                if (counter == 0) {
                                    counter++
                                    const id = btn.id.split("_")[3]
                                    const body = document.querySelector(`#open_post_content_${id}`)
                                    const content = body.textContent
                                    body.innerHTML = `<p><textarea name="new_text" id="edit_open_post_text_${id}" class="click_exempt form-control" rows="4">${content}</textarea><button id="save_open_changes_${id}" class="click_exempt my-2 btn btn-success save_open_changes_btns">Save</button></p>`
                                    const save_btns = document.querySelectorAll(".save_open_changes_btns")
                                    save_btns.forEach(save_btn => {
                                        const id = save_btn.id.split("_")[3]
                                        save_btn.addEventListener("click", function save_edit() {
                                            counter = 0
                                            const new_content = document.querySelector(`#edit_open_post_text_${id}`).value
                                            fetch(`/edit_post/${id}`, {
                                                method: "PUT",
                                                headers: { 'X-CSRFToken': csrftoken },
                                                body: JSON.stringify({ content: new_content })
                                            }).then(response => response.json())
                                                .then(data => {
                                                    body.innerHTML = `<p>${data["new_content"]}</p>`
                                                })
                                        })
                                    })
                                }
                            })
                        })


                    }).then(load_usernames)

                // Scroll to top
                window.scrollTo(0, 0);

            })
        })

        add_like_buttons(0);

        // Using index because once you load a post, it is still present in the show_all posts div, so there are 2 elements with the same id (because they are the same post)
        function add_like_buttons(index) {
            const like_button = document.querySelectorAll(".like_btns")
            // Adding event listener for each like button in the document
            like_button.forEach(button => {
                const id = button.id.split('_')[1]
                const posts_filtered = posts.filter(post => post["id"] == id)
                const post = posts_filtered[0]

                button.addEventListener("click", function () {

                    check_login().then(logged_in => {
                        // If user is not logged in , redirect to login page on click
                        if (logged_in) {
                            // Asks to like or unlike the post depending on action specified
                            if (post.liked) {
                                var action = "unlike"
                                post.liked = false
                            } else {
                                var action = "like"
                                post.liked = true
                            }
                            var post_div = document.querySelectorAll(`#post_${id}`)[index]
                            fetch(`/like_post/${id}`, {
                                method: "PUT",
                                headers: { 'X-CSRFToken': csrftoken },
                                body: JSON.stringify({ action: action })
                            }).then(function () {
                                // Show relevant button
                                button.querySelector("#like_btn").classList.toggle("d-none");
                                button.querySelector("#unlike_btn").classList.toggle("d-none");
                                fetch(`/get_post_like_count/${id}`)
                                    .then(response => response.json())
                                    .then(data => {
                                        var like_count = data["like_count"]
                                        post_div.querySelector(`#post_likes_${id}`).innerHTML = `${like_count} Likes`
                                    })
                            })
                        } else {
                            alert("You must be logged in to do that")
                            redirect_to_login()
                        }
                    })
                })
            })
        }

        const edit_btns = document.querySelectorAll(".edit_btns")
        edit_btns.forEach(btn => {
            var counter = 0
            btn.addEventListener("click", function edit_post() {
                if (counter == 0) {
                    counter++
                    const id = btn.id.split("_")[2]
                    const body = document.querySelectorAll(`#post_content_${id}`)[edit_index]
                    const content = body.textContent
                    console.log(content)
                    body.innerHTML = `<p><textarea name="new_text" id="edit_post_text_${id}" class="click_exempt form-control" rows="4">${content}</textarea><button id="save_changes_${id}" class="click_exempt my-2 btn btn-success save_changes_btns">Save</button></p>`
                    const save_btns = document.querySelectorAll(".save_changes_btns")
                    save_btns.forEach(save_btn => {
                        const id = save_btn.id.split("_")[2]
                        save_btn.addEventListener("click", function save_edit() {
                            counter = 0
                            const new_content = document.querySelector(`#edit_post_text_${id}`).value
                            fetch(`/edit_post/${id}`, {
                                method: "PUT",
                                headers: { 'X-CSRFToken': csrftoken },
                                body: JSON.stringify({ content: new_content })
                            }).then(response => response.json())
                                .then(data => {
                                    body.innerHTML = `<p>${data["new_content"]}</p>`
                                })
                        })
                    })
                }

            })

        })
    }


    function load_usernames() {
        const usernames = document.querySelectorAll('.username')
        usernames.forEach(username => {
            const id = username.id.split("_")[1]
            username.addEventListener("click", function () {
                load_user_profile(id)


            })
        })
    }


    function load_user_profile(id) {
        fetch(`/get_user_details/${id}`)
            .then(response => response.json())
            .then(data => {
                fetch(`/show_user_posts/${id}`)
                    .then(response => response.json())
                    .then(user_posts => {
                        check_login().then(logged_in => {
                            const user = data["user"]
                            check_follow_conditions(user["id"]).then(follow_data => {
                                const profile_div = document.querySelector("#show_user_profile")
                                profile_div.innerHTML = ""
                                const user_details_div = document.createElement('div')
                                user_details_div.classList = 'container-fluid'
                                if (logged_in == true && follow_data.is_self == false) {
                                    if (follow_data.is_followed) {
                                        var unfollow_d = ""
                                        var follow_d = "d-none"
                                    } else {
                                        var unfollow_d = "d-none"
                                        var follow_d = ""
                                    }
                                    var follow_btns = `<div class="my-2 p-2 text-center">
                        <span class="mx-2 ${follow_d}"><button id="follow_${user.id}" class="btn btn-success">Follow</button></span>
                        <span class="mx-2 ${unfollow_d}"><button id="unfollow_${user.id}" class="btn btn-danger">Unfollow</button></span></div>`

                                } else {
                                    var follow_btns = ""
                                }


                                user_details_div.innerHTML = `
                            <h3 id="user_${user.id}" class="click_exempt text-center username">${user.username}</h3>
                            <div class="my-1 text-center"><small class="text-muted">Joined : ${user.date_joined}</small></div>
                            <div class="my-1 text-center">
                            <span id="user_followers_${user.id}" class="mx-2">Followers : ${user.follower_count}</span>
                            <span id="user_following_${user.id}" class="mx-2">Following : ${user.following_count}</span>
                            </div>
                            `+ follow_btns + `<hr>`

                                const user_posts_div = document.createElement("div")
                                const posts_div_id = "show_user_profile_posts"
                                user_posts_div.id = posts_div_id

                                profile_div.append(user_details_div)

                                if (logged_in == true && follow_data.is_self == true) {
                                    follower_count_display = document.querySelector(`#user_followers_${id}`)
                                    follower_count_display.classList.add("clickable")
                                    var followers_container = document.createElement('div')
                                    followers_container.id = `followers_container`
                                    followers_container.classList = "d-none border container-fluid p-3";
                                    followers_container.style = "max-height:200px;overflow:auto;"
                                    fetch(`get_user_followers/${id}`)
                                        .then(response => response.json())
                                        .then(data => {
                                            const follower_array = data["followers"]
                                            follower_array.forEach(follower => {
                                                const follower_container = document.createElement('div')
                                                follower_container.classList = "mx-auto container-fluid border-bottom"
                                                follower_container.innerHTML = `
                                                    <span id="user_${follower.id}" class="click_exempt username">${follower.username}</span>
                                                `
                                                followers_container.append(follower_container)
                                            })
                                            user_details_div.append(followers_container)
                                        }).then(load_usernames)
                                    follower_count_display.addEventListener("click", () => {
                                        followers_container.classList.toggle("d-none")
                                    })
                                }


                                profile_div.append(user_posts_div)

                                if (logged_in == true && follow_data.is_self == false) {
                                    const follow_btn = document.querySelector(`#follow_${id}`)
                                    const unfollow_btn = document.querySelector(`#unfollow_${id}`)
                                    const follower_count_span = document.querySelector(`#user_followers_${id}`)
                                    load_follow_btn()
                                    load_unfollow_btn()
                                    function load_follow_btn() {
                                        follow_btn.addEventListener("click", () => {
                                            fetch(`/follow_user/${id}`, {
                                                method: "PUT",
                                                headers: { 'X-CSRFToken': csrftoken },
                                            }).then(response => function () {
                                                response.json()
                                            }).then(function () {
                                                follow_btn.parentElement.classList.add("d-none")
                                                unfollow_btn.parentElement.classList.remove("d-none")
                                                fetch(`/get_follower_count/${id}`)
                                                    .then(response => response.json())
                                                    .then(data => {
                                                        const fcount = data["follower_count"]
                                                        follower_count_span.innerHTML = `Followers : ${fcount}`
                                                    })
                                            })
                                        })
                                    }

                                    function load_unfollow_btn() {
                                        unfollow_btn.addEventListener("click", () => {
                                            fetch(`/unfollow_user/${id}`, {
                                                method: "PUT",
                                                headers: { 'X-CSRFToken': csrftoken },
                                            }).then(response => function () {
                                                response.json()
                                            }).then(function () {
                                                follow_btn.parentElement.classList.remove("d-none")
                                                unfollow_btn.parentElement.classList.add("d-none")
                                                fetch(`/get_follower_count/${id}`)
                                                    .then(response => response.json())
                                                    .then(data => {
                                                        const fcount = data["follower_count"]
                                                        follower_count_span.innerHTML = `Followers : ${fcount}`
                                                    })
                                            })
                                        })
                                    }
                                }


                                document.querySelector("#show_all_posts").classList.add("d-none")
                                document.querySelector("#show_post").classList.add("d-none")
                                document.querySelector("#show_user_profile").classList.remove("d-none")

                                load_given_posts(user_posts, posts_div_id, 1)
                            })

                        })
                    })
            })
    }

    check_login().then(logged_in => {
        if (logged_in) {
            document.querySelector("#following_page").addEventListener("click", load_following_page)
        }
    })
    function load_following_page() {
        fetch("/following_page")
            .then(response => response.json())
            .then(posts => {
                document.querySelector("#paginator").classList.add("d-none")
                document.querySelector('#all_posts').innerHTML = "<h2 class='mt-3 mb-0'>Following</h2>"
                load_given_posts(posts, "all_posts", 0)
                document.querySelector("#show_post").classList.add("d-none")
                document.querySelector("#show_user_profile").classList.add("d-none")
                document.querySelector("#show_all_posts").classList.remove('d-none')
            })

    }


    async function check_follow_conditions(user_id) {
        const response = await fetch(`/check_follow_conditions/${user_id}`)
        const data = await response.json()
        return data
    }


    async function get_pages_count() {
        const response = await fetch("/get_pages_count")
        const data = await response.json()
        const pages_count = data["pages_count"]
        return pages_count
    }


    get_pages_count().then(pages_count => {
        document.querySelector("#prev_page").addEventListener("click", function () {
            if (current_page == 1) {
                return
            } else {
                current_page--
                load_posts(current_page)
            }
        })

        document.querySelector("#next_page").addEventListener("click", function () {
            if (current_page == pages_count) {
                return
            } else {
                current_page++
                load_posts(current_page)
            }
        })
    })



})