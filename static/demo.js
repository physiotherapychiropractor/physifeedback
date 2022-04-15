import { RangeOfMotion } from './RangeOfMotion.js';
import { RepTimer } from './RepTimer.js';
import { RepetitionCounter } from './RepetitionCounter.js';


// Our input frames will come from here.
const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const controlsElement = document.getElementsByClassName('control-panel')[0];
const messageElement = document.getElementById('message');
const repCountElement = document.getElementById('repcount');
const setCountElement = document.getElementById('setcount');
const repTimeElement = document.getElementById('reptime');
const avgRepTimeElement = document.getElementById('avgreptime');
const leftRomElement = document.getElementById('leftrom');
const rightRomElement = document.getElementById('rightrom');
const leftRom2Element = document.getElementById('leftrom2');
const rightRom2Element = document.getElementById('rightrom2');
const avgLeftRomElement = document.getElementById('avgleftrom');
const avgRightRomElement = document.getElementById('avgrightrom');
const canvasCtx = canvasElement.getContext('2d');
const loaderElement = document.getElementsByClassName('loader')[0];
const tutorialVideoElement = document.getElementById('video');

// We'll add this to our control panel later, but we'll save it here so we can
// call tick() each time the graph runs.
const fpsControl = new FPS();
// Optimization: Turn off animated spinner after its hiding animation is done.
// const spinner = document.querySelector('.loading');
// spinner.ontransitionend = () => {
//   spinner.style.display = 'none';
// };

function zColor(data) {
  return 'white';
}

function getMotivation(repCount) {
     if (repCount == 0) {
       return 'Let\'s get started! Here\'s a demonstration of your chosen exercise:'
     }
     if (repCount ==1) {
        return 'Hooray! We\'ve gotten started!'
     }
     if (repCount == 5) {
        return 'You\'re silver!'
     }
     if (repCount== 9) {
        return 'You\'re gold!'
     }
     if (repCount > 9) {
        return 'Good job! Do you want to move onto a different exercise?'
     }
     return ''
}

async function onResults(results) {
    // Update the frame rate.
    fpsControl.tick();

    // Draw the overlays.
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.drawImage(
         results.image, 0, 0, canvasElement.width, canvasElement.height);

   if (sleep > 0) {
       loaderElement.hidden = false;
       sleep++;
       if (sleep > 10) {
           sleep = 0;
           loaderElement.hidden = true;
       }
       console.log('sleep');
   }
   else {
       if (frameCounter % 3 === 0 && reps.disabled) {
            fetch(fetchString,
                {
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    method: 'POST',
                    body: JSON.stringify({
                            pose_landmarks: results.poseLandmarks,
                            width: canvasElement.width,
                            height: canvasElement.height
                         })
                })
            .then((resp) => resp.json())
            .then(function(data) {
              var prev_count, curr_count, left, right, avg_left, avg_right, time, avg_time, new_count;

              prev_count = repCounter.n_repeats;
              prev_count = (prev_count % currentReps === 0 && prev_count !== 0) ? currentReps : (prev_count % currentReps);
                if (data['pose']) {
                  new_count = repCounter.repetitionCounter(data['pose']);
                  if (new_count === currentReps*currentSets) {
                      stopExercise();
                  }
                  curr_count = (new_count % currentReps === 0 && new_count !== 0) ? currentReps : (new_count % currentReps);
              } else {
                  curr_count = prev_count;
              }
              time = repTimer.repTimer(prev_count, curr_count);
              avg_time = repTimer.average();

              var rom1 = rom.rom(data['landmarks'], prev_count, curr_count);
              var avg_rom1 = rom.avgROM();

              [left, right] = rom1;
              [avg_left, avg_right] = avg_rom1;

              // console.log('rom: ' + rom1);
              // console.log('avg rom: ' + avg_rom1);
                setCountElement.innerHTML = (curr_count === currentReps ? Math.floor((new_count - 1) / currentReps) :  Math.floor(new_count / currentReps)) + 1 + "";
                repCountElement.innerHTML = curr_count;
                repTimeElement.innerHTML = time;
                avgRepTimeElement.innerHTML = avg_time;
                leftRomElement.style.width = left + '%';
                leftRom2Element.innerHTML = left + '%';
                rightRomElement.style.width = right + '%';
                rightRom2Element.innerHTML = right + '%';
                avgLeftRomElement.innerHTML = avg_left;
                avgRightRomElement.innerHTML = avg_right;
                // var motivation = getMotivation(curr_count);
                // if (motivation != '') {
                //     messageElement.innerHTML = motivation;
                // }
            })
        }
        if (results.poseLandmarks) {
              drawConnectors(
                  canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {
                    visibilityMin: 0.65,
                    color: 'white'
                  });
              drawLandmarks(
                  canvasCtx,
                  Object.values(POSE_LANDMARKS_LEFT)
                      .map(index => results.poseLandmarks[index]),
                  {visibilityMin: 0.65, color: zColor, fillColor: 'rgb(255,138,0)'});
              drawLandmarks(
                  canvasCtx,
                  Object.values(POSE_LANDMARKS_RIGHT)
                      .map(index => results.poseLandmarks[index]),
                  {visibilityMin: 0.65, color: zColor, fillColor: 'rgb(0,217,231)'});
              drawLandmarks(
                  canvasCtx,
                  Object.values(POSE_LANDMARKS_NEUTRAL)
                      .map(index => results.poseLandmarks[index]),
                  {visibilityMin: 0.65, color: zColor, fillColor: 'white'});
        }
        frameCounter++;
   }
    canvasCtx.restore();
}
var map = {
  'shoulderpress': 'https://www.youtube.com/embed/Bp3drI8ou98',
  'shoulderflexion': 'https://www.youtube.com/embed/NF1uwqc9VwU',
  'bridge': 'https://www.youtube.com/embed/l87SOtYxEec',
  'laterallegraise': 'https://www.youtube.com/embed/fNAu_PZfgsk',
  'hamstring': 'https://www.youtube.com/embed/-87ioKS6ulY',
};

// tutorialVideoElement.src = map[currentExercise];
var fetchString, repTimer, rom, repCounter;
// var fetchString = '/getpose?pose=' + currentExercise;
//
// var repTimer = new RepTimer();
// var rom = new RangeOfMotion(currentExercise);
// var repCounter = new RepetitionCounter(currentExercise + '_up');

const submitExerciseButton = document.getElementById('submitExerciseButton');
const reps = document.getElementById('pickreps');
const sets = document.getElementById('picksets');
const exs = document.getElementById('pickex');

var currentReps, currentSets;
var sleep = 1;
submitExerciseButton.addEventListener('click', () => {
    if (submitExerciseButton.innerText === "Start") {
        var currentExercise = exs.value;
        currentReps = reps.value;
        currentSets = sets.value;
        fetchString = '/getpose?pose=' + currentExercise;
        repTimer = new RepTimer();
        rom = new RangeOfMotion(currentExercise);
        repCounter = new RepetitionCounter(currentExercise + '_up');
        tutorialVideoElement.src = map[currentExercise];
        // var prev_count, curr_count, left, right, avg_left, avg_right, time, avg_time;
        // prev_count, curr_count, left, right, avg_left, avg_right
        sleep = 1;
        submitExerciseButton.innerText = "Stop";
        reps.disabled = true;
        sets.disabled = true;
        exs.disabled = true;
    } else {
        stopExercise();
    }
});


function stopExercise() {
    submitExerciseButton.innerText = "Start";
    reps.disabled = false;
    exs.disabled = false;
    sets.disabled = false;
}

var frameCounter = 0;

const pose = new Pose({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.3.1621277220/${file}`;
}});
pose.onResults(onResults);

/**
 * Instantiate a camera. We'll feed each frame we receive into the solution.
 */
const camera = new Camera(videoElement, {
  onFrame: async () => {
    await pose.send({image: videoElement});
  },
  // width: 960,
  // height: 540
});
camera.start();

//console.log(camera)
//console.log(fpsControl)
// Present a control panel through which the user can manipulate the solution
// options.
new ControlPanel(controlsElement, {
      selfieMode: true,
      modelComplexity: 1,
      smoothLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    })
    .add([
      new StaticText({title: 'MediaPipe Pose'}),
      fpsControl,
      new Toggle({title: 'Selfie Mode', field: 'selfieMode'}),
      new Slider({
        title: 'Model Complexity',
        field: 'modelComplexity',
        discrete: ['Lite', 'Full', 'Heavy'],
      }),
      new Toggle({title: 'Smooth Landmarks', field: 'smoothLandmarks'}),
      new Slider({
        title: 'Min Detection Confidence',
        field: 'minDetectionConfidence',
        range: [0, 1],
        step: 0.01
      }),
      new Slider({
        title: 'Min Tracking Confidence',
        field: 'minTrackingConfidence',
        range: [0, 1],
        step: 0.01
      }),
    ])
    .on(options => {
      videoElement.classList.toggle('selfie', options.selfieMode);
      pose.setOptions(options);
    });

    
    var resizeCanvas = function() {
      canvasElement.width = canvasElement.parentElement.clientWidth;
      canvasElement.height = 3 * canvasElement.width / 4;

      tutorialVideoElement.width = tutorialVideoElement.parentElement.clientWidth*0.85;
      tutorialVideoElement.height = 9 * tutorialVideoElement.width / 16;
    };

  window.addEventListener('resize', resizeCanvas, true);

  resizeCanvas();
  
